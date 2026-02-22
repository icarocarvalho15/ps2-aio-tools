import argparse

def main():
    parser = argparse.ArgumentParser(description="PS2 AIO Tools")
    parser.add_argument("--root", required=True, help="Caminho da raiz do USB")
    parser.add_argument("--ps2cfg", action="store_true", help="Gerar CFG PS2")
    parser.add_argument("--pops", action="store_true", help="Organizar POPS")
    parser.add_argument("--rename", action="store_true", help="Limpar nomes")

    args = parser.parse_args()

    print("Root:", args.root)
    print("Gerar CFG PS2:", args.ps2cfg)
    print("Organizar POPS:", args.pops)
    print("Renomear arquivos:", args.rename)

if __name__ == "__main__":
    main()