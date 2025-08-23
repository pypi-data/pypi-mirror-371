// sherpa-onnx/csrc/version.h
//
// Copyright      2025  Xiaomi Corporation

#include "sherpa-onnx/csrc/version.h"

namespace sherpa_onnx {

const char *GetGitDate() {
  static const char *date = "Sat Aug 23 03:45:52 2025";
  return date;
}

const char *GetGitSha1() {
  static const char *sha1 = "f25f1a5c";
  return sha1;
}

const char *GetVersionStr() {
  static const char *version = "0.0.7";
  return version;
}

}  // namespace sherpa_onnx
