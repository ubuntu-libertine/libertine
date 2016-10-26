# Copyright 2015-2016 Canonical Ltd.
#
# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License version 3, as published
# by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranties of
# MERCHANTABILITY, SATISFACTORY QUALITY, or FITNESS FOR A PARTICULAR
# PURPOSE.  See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program.  If not, see <http://www.gnu.org/licenses/>.

import os
import random
import shlex
import shutil
import signal
import string
import subprocess
import sys
import tempfile

from libertine import LibertineApplication
from libertine import LibertineContainer
from libertine import launcher

from contextlib import suppress
from io import StringIO
from selectors import DefaultSelector, EVENT_READ
from socket import socket, AF_UNIX, SOCK_STREAM
from testtools import TestCase, ExpectedException
from testtools.matchers import Equals, Not, Contains, MatchesPredicate
from threading import Thread, Barrier, BrokenBarrierError
from time import sleep
from unittest.mock import call, patch, MagicMock


def _generate_unique_string(prefix=''):
    """Generates a (hopefully) unique string."""
    return prefix + ''.join(random.choice(string.ascii_lowercase + string.digits) for i in range(8))


class TestLibertineLaunch(TestCase):
    def setUp(self):
        super(TestLibertineLaunch, self).setUp()
        self.cmake_source_dir = os.environ['CMAKE_SOURCE_DIR']
        self.cmake_binary_dir = os.environ['CMAKE_BINARY_DIR']

        container_config_path = os.path.join(self.cmake_binary_dir, 'tests', 'unit', 'libertine-config')

        # Set necessary enviroment variables
        os.environ['XDG_DATA_HOME'] = container_config_path
        os.environ['XDG_RUNTIME_DIR'] = tempfile.mkdtemp()
        os.environ['PATH'] = (self.cmake_source_dir + '/tests/mocks:' +
                              self.cmake_source_dir + '/tools:' + os.environ['PATH'])

        self.addCleanup(self.cleanup)

        # Lets figure out how to really mock this....
        cli_cmd = self.cmake_source_dir + '/tools/libertine-container-manager create -i test -n Test -t mock'
        args = shlex.split(cli_cmd)
        subprocess.Popen(args).wait()

    def cleanup(self):
        shutil.rmtree(os.environ['XDG_RUNTIME_DIR'])

    def test_launch_app_existing_container(self):
        '''
        Base line test to ensure launching an app in an existing container works.
        '''
        la = LibertineApplication('test', 'true')
        la.launch_application()

    def test_launch_app_nonexistent_container(self):
        '''
        Test to make sure that things gracefully handle a non-existing container.
        '''
        la = LibertineApplication('test1', 'true')
        self.assertRaises(RuntimeError, la.launch_application)

    def test_launch_good_app(self):
        '''
        Test to make sure that launching an app actually works.
        '''
        la = LibertineApplication('test', 'mock_app')
        la.launch_application()

    def test_launch_bad_app(self):
        '''
        Test to make sure launching an app that doesn't exist doesn't break things
        '''
        la = LibertineApplication('test', 'foo')
        self.assertRaises(FileNotFoundError, la.launch_application)


class TestLauncherTaskConfig(TestCase):
    """Unit tests for libertine.launcher.task module."""

    def test_task_config_ctor(self):
        """Verify Task constructor sets the required attributes."""
        fake_datum = [self.getUniqueString()]

        task = launcher.TaskConfig(launcher.TaskType.LAUNCH_SERVICE, fake_datum)

        self.assertThat(task.task_type, Equals(launcher.TaskType.LAUNCH_SERVICE))
        self.assertThat(task.datum, Equals(fake_datum))


class TestLauncherConfig(TestCase):
    """
    Verifies the defined behaviour of the Libertine Launcher Config class.
    """

    # a standard set of command-line arguments for when we don't care
    id_arg = ['-i', 'container-id']
    exec_args = ['exec-line', 'one', 'two', 'three']
    basic_args = id_arg + exec_args

    def test_unqiue_id_generation(self):
        """Ensure each unique configuration has a unique identifier."""
        config1 = launcher.Config(TestLauncherConfig.basic_args[:])
        config2 = launcher.Config(TestLauncherConfig.basic_args[:])
        self.assertThat(config1.id, Not(Equals(config2.id)))

    def test_mandatory_args(self):
        """Verify that the mandatory CLI args get put where they're supposed to get put."""
        config = launcher.Config(TestLauncherConfig.basic_args[:])
        self.assertEquals(config.exec_line, TestLauncherConfig.exec_args)

    @patch('sys.stderr', new_callable=StringIO)
    def test_missing_mandatory_args(self, stderr):
        """Make sure missing mandatory CLI args are handled gracefully.

        Gracefully means a usage message is printed and the application exists.
        """
        with ExpectedException(SystemExit):
            config = launcher.Config(TestLauncherConfig.id_arg)
        message = stderr.getvalue().strip()
        self.assertThat(message, Contains("usage:"))

    def test_optional_id_arg(self):
        """Make sure optional container id is handled."""
        config = launcher.Config(TestLauncherConfig.basic_args[:])
        self.assertEquals(config.container_id, 'container-id')

    def test_missing_optional_id_arg(self):
        """Ensure command parsing works fine when container id is left off"""
        config = launcher.Config(TestLauncherConfig.exec_args)
        self.assertEquals(config.container_id, None)

    def test_one_explicit_environment_arg(self):
        """Verify that one -E arg gets put into the environment."""
        argv = ['-EMY_ENV=something'] + TestLauncherConfig.basic_args[:]
        config = launcher.Config(argv)
        self.assertIn('MY_ENV', config.session_environ)

    def test_two_explicit_environment_args(self):
        """Verify that multiple -E args gets put into the environment."""
        argv = ['-EMY_ENV=something', '-E', 'SOME_OTHER_ENV=somethingelse'] + TestLauncherConfig.basic_args[:]
        config = launcher.Config(argv)
        self.assertEquals(config.session_environ.get('MY_ENV', 'nothing'), 'something')
        self.assertEquals(config.session_environ.get('SOME_OTHER_ENV', 'nothing'), 'somethingelse')

    def test_usr_games_is_in_path(self):
        """Makes sure that /usr/games is in $PATH.

        This was a problem encountered early on.
        """
        with patch.dict('os.environ', {'PATH': '/usr/local/bin:/bin:/usr/bin'}):
            self.assertNotIn('/usr/games', os.environ['PATH'].split(sep=':'))
            config = launcher.Config(TestLauncherConfig.basic_args[:])
            self.assertIn('/usr/games', config.session_environ['PATH'].split(sep=':'))

    def test_maliit_socket_bridge_from_env(self):
        """Make sure the Maliit socket bridge gets configured.

        The Maliit socket address is normally found in an environment variable.
        """
        env_key = 'MALIIT_SERVER_ADDRESS'
        bogus_host_address = 'unix:abstract=/tmp/maliit-host-socket'
        maliit_bridge = None

        with patch.dict('os.environ', {env_key: bogus_host_address}):
            config = launcher.Config(TestLauncherConfig.basic_args[:])
            for bridge in config.socket_bridges:
                if bridge.env_var == env_key:
                    maliit_bridge = bridge

        self.assertIsNotNone(maliit_bridge)
        self.assertThat(maliit_bridge.host_address, Equals(bogus_host_address))
        self.assertThat(maliit_bridge.session_address, Contains('maliit'))
        self.assertThat(config.session_environ.get(env_key, None), Not(Equals(None)))
        self.assertThat(config.session_environ.get(env_key, bogus_host_address),
                        Not(Equals(bogus_host_address)))

    def test_dbus_socket_bridge_from_env(self):
        """Make sure the D-Bus socket bridge gets configured.

        The D-Bus socket address is normally found in an environment variable.
        """
        env_key = 'DBUS_SESSION_BUS_ADDRESS'
        bogus_host_address = 'unix:abstract=/tmp/dbus-host-socket'
        dbus_bridge = None

        with patch.dict('os.environ', {env_key: bogus_host_address}):
            config = launcher.Config(TestLauncherConfig.basic_args[:])
            for bridge in config.socket_bridges:
                if bridge.env_var == env_key:
                    dbus_bridge = bridge

        self.assertIsNotNone(dbus_bridge)
        self.assertThat(dbus_bridge.host_address, Equals(bogus_host_address))
        self.assertThat(dbus_bridge.session_address, Contains('dbus'))
        self.assertThat(config.session_environ.get(env_key, None), Not(Equals(None)))
        self.assertThat(config.session_environ.get(env_key, bogus_host_address),
                        Not(Equals(bogus_host_address)))

    def test_default_prelaunch_tasks(self):
        """Ensure 'pasted' is in the default pre-launch task list."""
        def pasted_is_in_list(task_list):
            for t in task_list:
                if t.task_type == launcher.TaskType.LAUNCH_SERVICE and t.datum[0] == "pasted":
                    return True
            return False

        config = launcher.Config(TestLauncherConfig.basic_args[:])
        self.assertThat(config.prelaunch_tasks,
                        MatchesPredicate(pasted_is_in_list, "pasted is not in task list"))


class TestLauncherSession(TestCase):
    """
    Verifies the defined bahaviour of a Libertine Lunacher session.

    This set of tests does the alien probe dance on things that can be verified
    without actually requiring the launcher event loop be runing -- except for
    the basic check that an event loop runs and can be terminated.
    """

    def setUp(self):
        """Set up a mock config and a mock container."""
        super().setUp()

        fake_session_socket = 'unix:path=/tmp/garbage'
        fake_bridge_config = launcher.SocketBridge('FAKE_SOCKET', 'dummy', fake_session_socket)
        self._mock_config = MagicMock(spec=launcher.Config,
                                      socket_bridges=[fake_bridge_config])

        self._fake_session_address = launcher.translate_to_real_address(fake_session_socket)

        self._mock_container = MagicMock(spec=LibertineContainer)

    def test_basic_ctor(self):
        """Just test the basic no-frill construction of a session."""
        self._mock_config.id = 'blah'
        session = launcher.Session(self._mock_config, self._mock_container)
        self.assertThat(session.id, Equals('blah'))

    def test_signals_are_restored(self):
        """Verify that a Session object, when used correctly, cleans up any signal
        handlers it has replaced.

        This test just makes sure the test environment is left in a clean state
        after testing so that it does not corrupt the results of other unit
        tests.
        """
        old_sigchld_handler = signal.getsignal(signal.SIGCHLD)
        old_sigint_handler  = signal.getsignal(signal.SIGINT)
        old_sigterm_handler = signal.getsignal(signal.SIGTERM)

        with launcher.Session(self._mock_config, self._mock_container) as session:
            pass

        self.assertThat(signal.getsignal(signal.SIGCHLD), Equals(old_sigchld_handler))
        self.assertThat(signal.getsignal(signal.SIGINT),  Equals(old_sigint_handler))
        self.assertThat(signal.getsignal(signal.SIGTERM), Equals(old_sigterm_handler))

    @patch('libertine.launcher.session.socket.listen')
    @patch('libertine.launcher.session.socket.bind')
    def test_bridge_listener_is_created(self, mock_bind, mock_listen):
        """Verify that a socket connection listener is set up for a socket bridge config passed in."""
        with launcher.Session(self._mock_config, self._mock_container) as session:
            self.assertThat(mock_bind.call_args, Equals(call(self._fake_session_address)))
            self.assertThat(mock_listen.called, Equals(True))

    def test_sigchld_exits_run(self):
        """Verify that the run() method returns on receipt of SIGCHLD. """
        with launcher.Session(self._mock_config, self._mock_container) as session:
            def run_session_event_loop():
                session.run()

            session_event_loop = Thread(target=run_session_event_loop)
            session_event_loop.start()

            os.kill(os.getpid(), signal.SIGCHLD)

            session_event_loop.join(timeout=0.5)
            self.assertThat(session_event_loop.is_alive(), Equals(False))

    def test_sigint_exits_run(self):
        """Verify that the run() method returns on receipt of SIGINT. """
        with launcher.Session(self._mock_config, self._mock_container) as session:
            def run_session_event_loop():
                session.run()

            session_event_loop = Thread(target=run_session_event_loop)
            session_event_loop.start()

            os.kill(os.getpid(), signal.SIGINT)

            session_event_loop.join(timeout=0.5)
            self.assertThat(session_event_loop.is_alive(), Equals(False))

    def test_sigterm_exits_run(self):
        """Verify that the run() method returns on receipt of SIGTERM."""
        with launcher.Session(self._mock_config, self._mock_container) as session:
            def run_session_event_loop():
                session.run()

            session_event_loop = Thread(target=run_session_event_loop)
            session_event_loop.start()

            os.kill(os.getpid(), signal.SIGTERM)

            session_event_loop.join(timeout=0.5)
            self.assertThat(session_event_loop.is_alive(), Equals(False))


class TestLauncherServiceTask(TestCase):
    """Verify the expected bahaviour of launch tasks."""

    def setUp(self):
        """Set up an even loop fixture to watch for signals from spawned tasks. """
        super().setUp()
        self._sigchld_caught = False

        def noopSignalHandler(*args):
            pass
        original_sigchld_handler = signal.signal(signal.SIGCHLD, noopSignalHandler)
        self.addCleanup(lambda: signal.signal(signal.SIGCHLD, original_sigchld_handler))

        sig_r_fd, sig_w_fd = os.pipe2(os.O_NONBLOCK | os.O_CLOEXEC)
        signal.set_wakeup_fd(sig_w_fd)

        pre_loop_barrier = Barrier(2)
        self._post_loop_barrier = Barrier(2)

        def loop():
            pre_loop_barrier.wait(1)
            selector = DefaultSelector()
            selector.register(sig_r_fd, EVENT_READ)
            with suppress(StopIteration):
                while True:
                    events = selector.select(timeout=5)
                    if len(events) == 0:
                        raise StopIteration
                    for key, mask in events:
                        if key.fd == sig_r_fd:
                            data = os.read(sig_r_fd, 4)
                            self._sigchld_caught = True
                            raise StopIteration
            self._post_loop_barrier.wait(1)

        test_loop = Thread(target=loop)
        self.addCleanup(lambda: test_loop.join(1))
        test_loop.start()
        pre_loop_barrier.wait(1)

    def test_service_sends_SIGCHLD_on_exit(self):
        """Verify a SIGCHLD signal gets raised when the service exits.

        Runs a fast-exiting 'service' (which should finish on its own in a
        reasonable time) and verifies that a SIGCHLD is raised.
        """
        config = launcher.TaskConfig(launcher.TaskType.LAUNCH_SERVICE, ("/bin/true"))
        task = launcher.LaunchServiceTask(config)
        task.start()
        self._post_loop_barrier.wait(1)
        self.assertThat(self._sigchld_caught, Equals(True))
        
    def test_service_stop_exits_program(self):
        """Verify the service exists when stopped.
        
        Runs a long-running service (which should not normally finish on its
        own) and verifies that a SIGCHLD is received after calling stop() on the
        task.
        """
        config = launcher.TaskConfig(launcher.TaskType.LAUNCH_SERVICE, ("/usr/bin/yes"))
        task = launcher.LaunchServiceTask(config)
        task.start()
        sleep(0.05)
        task.stop()
        self._post_loop_barrier.wait(1)
        self.assertThat(self._sigchld_caught, Equals(True))


class SessionEventLoopRunning(Thread):
    """Provide a running, stoppable session event loop as a context manager thread."""

    def __init__(self, session):
        super().__init__()
        self._session = session

    def __enter__(self):
        """Start the session event loop thread running on context entry."""
        self.start()
        return self

    def __exit__(self, *exc):
        """Shut down the session event loop thread."""
        join_attempt_count = 0
        max_join_attempts = 5
        while self.is_alive() and join_attempt_count < max_join_attempts:
            self.stop()
            self.join(timeout=0.5)
            join_attempt_count += 1
        assert join_attempt_count < max_join_attempts
        return False

    def run(self):
        with suppress(BrokenBarrierError):
            self._session.run()

    def stop(self):
        """Stop the session event loop.

        May be called multiple times without harm.

        Has a little nap after raising the TERM signal so the GIL gets
        relinquished and the loop thread has a chance to process its signals.
        """
        os.kill(os.getpid(), signal.SIGTERM)
        sleep(0.0001)


class EchoServer(Thread):
    """A test fixture providing some kind of service running on the host at a known address."""

    socket_address = 'unix:path=/tmp/echo-host-' + _generate_unique_string()

    def __init__(self):
        super().__init__()
        self.daemon = True

        real_socket_address = launcher.translate_to_real_address(EchoServer.socket_address)

        self._socket = socket(AF_UNIX, SOCK_STREAM)
        self._socket.bind(real_socket_address)
        self._socket.listen(5)
        self.start()

    def run(self):
        while True:
            (s, a) = self._socket.accept()
            b = s.recv(512)
            r = bytes("echo<<{}>>".format(b), 'ascii')
            with suppress(BrokenPipeError):
                s.sendall(r)
            s.close()


class TestLauncherSessionSocketBridge(TestCase):
    """Verify the Launcher Session socket bridge functionality."""

    _fake_session_socket = 'unix:path=/tmp/session-' + _generate_unique_string()

    @patch('test_launcher.LibertineContainer')
    def setUp(self, mock_container):
        """Construct a test fixture with a single socket bridge configuration."""
        super().setUp()

        real_socket_address = launcher.translate_to_real_address(self._fake_session_socket)
        with suppress(OSError):
            os.remove(real_socket_address)

        config = MagicMock(spec=launcher.Config,
                           socket_bridges=[launcher.SocketBridge('FAKE_SOCKET',
                                           host_address=EchoServer.socket_address,
                                           session_address=self._fake_session_socket)])
        self._session = launcher.Session(config, mock_container)

    def test_abstract_socket_is_used(self):
        bogus_abstract_path = '/tmp/dbus-host-socket'
        bogus_host_address = 'unix:abstract=' + bogus_abstract_path

        bogus_host_socket = launcher.translate_to_real_address(bogus_host_address)

        self.assertThat(bogus_host_socket, Equals('\0' + bogus_abstract_path))

    def test_connection_acceptance(self):
        """Verify that when at attempt is made to connect to a session bridge it is accepted.

        This test has to perform some ear-wiggling and hop-dart behaviour to
        make sure it waits until the event loop has called the accept() method
        before it tries to check to see if the accept() method has been called
        (hence the thread barrier).  Also, because the real socket accept
        operation does not get performed, the mock accept() call can be
        executed several times by the server before we get around to actually
        checking up on it and we only care that it's called at least once, hence
        the 'called_once' flag.
        """
        barrier = Barrier(2, timeout=0.5)
        called_once = False
        real_session_address = launcher.translate_to_real_address(self._fake_session_socket)

        def fake_accept(*args, called_once=called_once):
            if not called_once:
                called_once = True
                barrier.wait()
            sock = socket(AF_UNIX, SOCK_STREAM)
            return (sock, 'xyzzy')

        with patch('libertine.launcher.session.socket.accept', side_effect=fake_accept) as mock_accept:
            with SessionEventLoopRunning(self._session):
                sock = socket(AF_UNIX, SOCK_STREAM)
                sock.connect(real_session_address)
                with suppress(BrokenBarrierError):
                    barrier.wait()
            self.assertThat(mock_accept.called, Equals(True), "accept() not called")

    def test_bridge_socket_relay(self):
        """Test that the whole socket bridge relay functionality works.

        Sure, this is not really a unit test but a black-box functional test.
        """
        echo_server = EchoServer()
        real_session_address = launcher.translate_to_real_address(self._fake_session_socket)

        with SessionEventLoopRunning(self._session):
            sock = socket(AF_UNIX, SOCK_STREAM)
            sock.connect(real_session_address)
            sock.sendall(bytes('ping', 'ascii'))
            response = str(sock.recv(1024), 'ascii')
            self.assertThat(response, Contains('ping'))


class TestLauncherSessionTask(TestCase):
    """Verify how a Session handles Tasks."""

    @patch('test_launcher.LibertineContainer')
    def setUp(self, mock_container):
        super().setUp()

        # Monkey-patch the task object created by the LaunchServiceTask class.
        # This is a little awkward by it's the way Python works.
        p = patch('libertine.launcher.session.LaunchServiceTask')
        mock_service_task_class = p.start()
        self._mock_service_task = mock_service_task_class.return_value
        self._mock_service_task.wait = MagicMock(return_value=True)
        self.addCleanup(p.stop)

        fake_datum = [self.getUniqueString()]
        task = launcher.TaskConfig(launcher.TaskType.LAUNCH_SERVICE, fake_datum)

        config = MagicMock(spec=launcher.Config, socket_bridges=[], prelaunch_tasks=[task], host_environ={})
        self._session = launcher.Session(config, mock_container)

    def test_session_starts_prelaunch_task(self):
        """Test that a session starts a pre-launch task."""
        self.assertThat(self._mock_service_task.start.called,
                        Equals(True),
                        message="task.start() not called")

    def test_session_stops_prelaunch_task(self):
        """Test that a session starts a pre-launch task."""
        with SessionEventLoopRunning(self._session) as event_loop:
            event_loop.stop()
        self.assertThat(self._mock_service_task.stop.called, Equals(True))

    def test_session_handles_dying_prelaunch_task(self):
        """Test that a session starts a pre-launch task."""
        with SessionEventLoopRunning(self._session) as event_loop:
            os.kill(os.getpid(), signal.SIGCHLD)
            event_loop.stop()
        self.assertThat(self._mock_service_task.wait.called, Equals(True))


class TestLauncherContainerBehavior(TestCase):
    """Verify some expected behaviour when it comes to running the contained application."""

    def setUp(self):
        super().setUp()

        self._mock_config = MagicMock(spec=launcher.Config,
                                      socket_bridges=[],
                                      session_environ={})

        # Need to fake the ContainersConfig used internally by
        # LibertineContainer...  that whole outfit needs to be refactored for
        # better testing next.
        mock_containers_config = MagicMock()
        mock_containers_config.get_container_type = MagicMock(return_value='mock')

        self._container_proxy = LibertineContainer(container_id='xyzzy',
                                                   containers_config=mock_containers_config)

        libertine_mock_patcher = patch.object(self._container_proxy, "container", autospec=True)
        self._mock_container = libertine_mock_patcher.start()
        self.addCleanup(libertine_mock_patcher.stop)

    def test_start_application(self):
        """Test the start_application() function of the session API."""
        self._mock_config.exec_line = ["/bin/echo", "sis", "boom", "bah"]

        with launcher.Session(self._mock_config, self._container_proxy) as session:
            with SessionEventLoopRunning(session):
                session.start_application()

        #self.assertThat(self._mock_container.connect.called, Equals(True))
        #self.assertThat(self._mock_container.disconnect.called, Equals(True))
        self.assertThat(self._mock_container.start_application.called, Equals(True))
        self.assertThat(self._mock_container.start_application.call_args[0][0],
                        Equals(self._mock_config.exec_line))
        self.assertThat(self._mock_container.finish_application.called, Equals(True))

    def test_environment_gets_set(self):
        """Verify that the configured variables are set in the contained execution environments."""
        fake_value = _generate_unique_string()
        fake_var = _generate_unique_string(prefix='V')
        self._mock_config.session_environ[fake_var] = fake_value
        self._mock_config.exec_line = ["/dev/null"]

        with launcher.Session(self._mock_config, self._container_proxy) as session:
            with SessionEventLoopRunning(session):
                session.start_application()

        self.assertThat(self._mock_container.start_application.call_args[0][1], Contains(fake_var))
