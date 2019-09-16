#!/usr/bin/env python
# -*- coding: utf-8 -*-

from conans import ConanFile, CMake, tools
import os


class SRTConan(ConanFile):
    name = "srt"
    version = "1.3.1"
    description = "Secure, Reliable, Transport"
    url = "https://github.com/bincrafters/conan-srt"
    homepage = "https://www.srtalliance.org/"
    author = "Bincrafters <bincrafters@gmail.com>"
    license = "MPL-2.0"

    # Packages the license for the conanfile.py
    exports = ["LICENSE.md"]

    # Remove following lines if the target lib does not use cmake.
    exports_sources = ["CMakeLists.txt"]
    generators = "cmake"

    # Options may need to change depending on the packaged library.
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {'shared': False, 'fPIC': True}

    _source_subfolder = "source_subfolder"
    _build_subfolder = "build_subfolder"

    def requirements(self):
        self.requires.add('openssl/1.0.2t')
        if self.settings.os == 'Windows':
            self.requires.add('pthread-win32/2.9.1@bincrafters/stable')

    def config_options(self):
        if self.settings.os == 'Windows':
            del self.options.fPIC

    def source(self):
        source_url = "https://github.com/Haivision/srt"
        tools.get("{0}/archive/v{1}.tar.gz".format(source_url, self.version))
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

        if self.settings.os == "Linux":
            tools.replace_in_file(os.path.join(self._source_subfolder, 'CMakeLists.txt'),
                                  'set (SSL_LIBRARIES ${OPENSSL_LIBRARIES})',
                                  'set (SSL_LIBRARIES ${OPENSSL_LIBRARIES} dl)')

        tools.replace_in_file(os.path.join(self._source_subfolder, 'CMakeLists.txt'),
                              'srt_add_application(srt-multiplex ${VIRTUAL_srtsupport})',
                              '#srt_add_application(srt-multiplex ${VIRTUAL_srtsupport})')
        tools.replace_in_file(os.path.join(self._source_subfolder, 'CMakeLists.txt'),
                              'srt_add_application(srt-file-transmit ${VIRTUAL_srtsupport})',
                              '#srt_add_application(srt-file-transmit ${VIRTUAL_srtsupport})')

    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions['CMAKE_INSTALL_LIBDIR'] = 'lib'
        cmake.definitions['CMAKE_INSTALL_BINDIR'] = 'bin'
        cmake.definitions['CMAKE_INSTALL_INCLUDEDIR'] = 'include'
        cmake.definitions['ENABLE_SHARED'] = self.options.shared
        cmake.definitions['ENABLE_STATIC'] = not self.options.shared
        cmake.definitions['ENABLE_DEBUG'] = self.settings.build_type == 'Debug'

        cmake.definitions['OPENSSL_ROOT_DIR'] = self.deps_cpp_info['OpenSSL'].rootpath
        cmake.definitions['OPENSSL_INCLUDE_DIR'] = self.deps_cpp_info['OpenSSL'].include_paths[0]
        cmake.definitions['OPENSSL_LIB_DIR'] = self.deps_cpp_info['OpenSSL'].lib_paths[0]
        cmake.definitions['OPENSSL_LIBRARIES'] = ';'.join(self.deps_cpp_info['OpenSSL'].libs)

        if self.settings.os == 'Windows':
            cmake.definitions['PTHREAD_INCLUDE_DIR'] = self.deps_cpp_info['pthread-win32'].include_paths[0]
            cmake.definitions['PTHREAD_LIBRARY'] = self.deps_cpp_info['pthread-win32'].libs[0]

        if self.settings.os != 'Windows':
            cmake.definitions['CMAKE_POSITION_INDEPENDENT_CODE'] = self.options.fPIC
        cmake.configure(build_folder=self._build_subfolder)
        return cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()

    def package_info(self):
        if self.settings.os == 'Windows':
            self.cpp_info.libs = ['srt' if self.options.shared else 'srt_static']
        else:
            self.cpp_info.libs = ['srt']
        if self.settings.os == 'Linux':
            self.cpp_info.libs.append('pthread')
