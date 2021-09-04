{ buildGoModule, fetchFromGitHub, ... }:
buildGoModule rec {
  pname = "torrentfs";
  version = "1.31.0";
  src = fetchFromGitHub {
    owner = "anacrolix";
    repo = "torrent";
    rev = "v${version}";
    sha256 = "11ymcjjq4vmfin4fac7hqjn361krrqqpm6psnkwh5qsi11wndjwg";
  };
  vendorSha256 = "03a3x60ndzw3ild9h28wy5zkccd2sfqgg2rqdx6zi20b3x1bb0jf";
  subPackages = [ "cmd/torrentfs" ];
}
