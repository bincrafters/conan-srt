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
    default_options = "shared=False", "fPIC=True"

    source_subfolder = "source_subfolder"
    build_subfolder = "build_subfolder"

    def requirements(self):
        self.requires.add('OpenSSL/1.0.2o@conan/stable')

    def config_options(self):
        if self.settings.os == 'Windows':
            del self.options.fPIC

    def source(self):
        source_url = "https://github.com/Haivision/srt"
        tools.get("{0}/archive/v{1}.tar.gz".format(source_url, self.version))
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self.source_subfolder)

        if self.settings.os == "Linux":
            tools.replace_in_file(os.path.join(self.source_subfolder, 'CMakeLists.txt'),
                                  'set (SSL_LIBRARIES ${OPENSSL_LIBRARIES})',
                                  'set (SSL_LIBRARIES ${OPENSSL_LIBRARIES} dl)')

    def configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions['ENABLE_SHARED'] = self.options.shared
        cmake.definitions['ENABLE_STATIC'] = not self.options.shared
        cmake.definitions['ENABLE_DEBUG'] = self.settings.build_type == 'Debug'

        cmake.definitions['OPENSSL_ROOT_DIR'] = self.deps_cpp_info['OpenSSL'].rootpath
        cmake.definitions['OPENSSL_INCLUDE_DIR'] = self.deps_cpp_info['OpenSSL'].include_paths[0]
        cmake.definitions['OPENSSL_LIB_DIR'] = self.deps_cpp_info['OpenSSL'].lib_paths[0]
        cmake.definitions['OPENSSL_LIBRARIES'] = ';'.join(self.deps_cpp_info['OpenSSL'].libs)

        if self.settings.os != 'Windows':
            cmake.definitions['CMAKE_POSITION_INDEPENDENT_CODE'] = self.options.fPIC
        cmake.configure(build_folder=self.build_subfolder)
        return cmake

    def build(self):
        cmake = self.configure_cmake()
        cmake.build()

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses", src=self.source_subfolder)
        cmake = self.configure_cmake()
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ['srt']
        if self.settings.os == 'Linux':
            self.cpp_info.libs.append('pthread')
