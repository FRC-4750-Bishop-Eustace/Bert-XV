{
  description = "Source code for Beʳᵗ 15";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
  };

  outputs = { nixpkgs, ... }:
    let
      systems = [
        "x86_64-linux"
        "aarch64-linux"
      ];

      forAllSystems = nixpkgs.lib.genAttrs systems;
    in {
      devShells = forAllSystems (system:
        let
          pkgs = import nixpkgs {
            inherit system;
          };
        in {
          default = pkgs.mkShell {
            packages = with pkgs; [
              python3
              stdenv.cc.cc.lib
              gcc
              pkg-config

              # Wayland
              wayland
              wayland-protocols
              wayland-scanner
              libxkbcommon
              libdecor

              # X11
              libX11
              libXext
              libXcursor
              libXfixes
              libXi
              libXrandr
              libXScrnSaver
              libXtst

              # XCB
              libxcb
              xcbutil
              xcbutilwm
              xcbutilimage
              xcbutilkeysyms

              # Graphics
              libGL
              libgbm

              # Hardware
              dbus
              libusb1
            ];

            # Expose native libraries to dynamically linked applications
            LD_LIBRARY_PATH = pkgs.lib.makeLibraryPath (with pkgs; [
              stdenv.cc.cc.lib

              # Wayland
              wayland
              libxkbcommon
              libdecor

              # X11
              libX11
              libXext
              libXcursor
              libXfixes
              libXi
              libXrandr
              libXScrnSaver
              libXtst
              libxcb
              xcbutil
              xcbutilwm
              xcbutilimage
              xcbutilkeysyms

              # Graphics
              libGL
              libgbm
            ]);
          };
        });
    };
}
