// sherpa-onnx/csrc/version.h
//
// Copyright      2025  Xiaomi Corporation

#include "sherpa-onnx/csrc/version.h"

namespace sherpa_onnx {

const char *GetGitDate() {
  static const char *date = "Sun Aug 24 08:23:41 2025";
  return date;
}

const char *GetGitSha1() {
  static const char *sha1 = "b546f2d3";
  return sha1;
}

const char *GetVersionStr() {
  static const char *version = "0.0.15";
  return version;
}

}  // namespace sherpa_onnx
