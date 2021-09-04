{ pkgs ? import <nixpkgs> {} }:
pkgs.mkShell {
  buildInputs = with pkgs; [
    (python3.withPackages (ps: [
      ps.aiodns
      ps.aiohttp
      ps.asgiref
      ps.cchardet
      ps.django_3
      ps.jedi
      ps.lxml
      ps.mypy
      ps.pylint
    ]))
    (callPackage ./torrentfs.nix {})
    mpv
  ];
}
