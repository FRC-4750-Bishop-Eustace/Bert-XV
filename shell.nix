{ pkgs ? import <nixpkgs> {} }:

pkgs.mkShell {
  packages = with pkgs; [
    python3
    stdenv.cc.cc.lib
    gcc
    pkg-config
  ];

  shellHook = ''
    export LD_LIBRARY_PATH="${pkgs.stdenv.cc.cc.lib}/lib:$LD_LIBRARY_PATH"

    echo "RobotPy development environment"
    echo "Python: $(python3 --version)"
  '';
}
