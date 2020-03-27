import os

from conans import ConanFile, CMake, tools

class LibspatialindexConan(ConanFile):
    name = "libspatialindex"
    description = "C++ implementation of R*-tree, an MVR-tree and a TPR-tree with C API."
    license = "MIT"
    topics = ("conan", "libspatialindex", "spatial-indexing", "tree")
    homepage = "https://github.com/libspatialindex/libspatialindex"
    url = "https://github.com/conan-io/conan-center-index"
    exports_sources = ["CMakeLists.txt", "patches/**"]
    generators = "cmake"
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}

    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename(self.name + "-" + self.version, self._source_subfolder)

    def build(self):
        for patch in self.conan_data["patches"][self.version]:
            tools.patch(**patch)
        tools.replace_in_file(os.path.join(self._source_subfolder, "CMakeLists.txt"),
                              "spatialindex-64", "spatialindex")
        tools.replace_in_file(os.path.join(self._source_subfolder, "CMakeLists.txt"),
                              "spatialindex_c-64", "spatialindex_c")
        tools.replace_in_file(os.path.join(self._source_subfolder, "CMakeLists.txt"),
                              "spatialindex-32", "spatialindex")
        tools.replace_in_file(os.path.join(self._source_subfolder, "CMakeLists.txt"),
                              "spatialindex_c-32", "spatialindex_c")
        cmake = self._configure_cmake()
        cmake.build()

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["SIDX_BUILD_TESTS"] = False
        self._cmake.definitions["SIDX_BIN_SUBDIR"] = "bin"
        self._cmake.definitions["SIDX_LIB_SUBDIR"] = "lib"
        self._cmake.definitions["SIDX_INCLUDE_SUBDIR"] = "include"
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def package(self):
        self.copy("COPYING", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ["spatialindex_c", "spatialindex"]
        if self.settings.os == "Linux":
            self.cpp_info.system_libs.append("m")
