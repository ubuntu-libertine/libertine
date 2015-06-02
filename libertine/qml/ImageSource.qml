/**
 * @file ImageSource.qml
 * @brief Libertine image source module
 */
/*
 * Copyright 2015 Canonical Ltd
 *
 * Libertine is free software: you can redistribute it and/or modify it under
 * the terms of the GNU General Public License, version 3, as published by the
 * Free Software Foundation.
 *
 * Libertine is distributed in the hope that it will be useful, but WITHOUT ANY
 * WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
 * A PARTICULAR PURPOSE.  See the GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program.  If not, see <http://www.gnu.org/licenses/>.
 */
import QtQml 2.2
import "image_sources.js" as ImageSources


/**
 * A simple structure describing the image source from which a container may be
 * built.
 */
QtObject {
    property string name

    /**
     * Gets the default image source (if any).
     * @return type:ImageSource the default image source
     */
    function defaultSource() {
        return ImageSources.availableSources[0]
    }

    /**
     * Loads the available image sources from an external configuration file.
     * @return array of image sources
     */
    function loadSources() {
        return ImageSources.availableSources
    }
}
