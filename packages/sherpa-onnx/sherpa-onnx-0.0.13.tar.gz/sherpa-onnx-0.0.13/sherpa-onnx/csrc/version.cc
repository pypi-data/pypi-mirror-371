// sherpa-onnx/csrc/version.h
//
// Copyright      2025  Xiaomi Corporation

#include "sherpa-onnx/csrc/version.h"

namespace sherpa_onnx {

const char *GetGitDate() {
  static const char *date = "Sun Aug 24 01:20:21 2025";
  return date;
}

const char *GetGitSha1() {
  static const char *sha1 = "45cbf510";
  return sha1;
}

const char *GetVersionStr() {
  static const char *version = "0.0.13";
  return version;
}

}  // namespace sherpa_onnx
