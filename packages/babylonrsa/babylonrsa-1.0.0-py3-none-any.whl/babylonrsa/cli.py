import argparse, sys
from .rsa import *

def main():
    parser = argparse.ArgumentParser(prog="babylonrsa", description="BabylonRSA CLI (Base-60 RSA)")
    sub = parser.add_subparsers(dest="cmd")

    g = sub.add_parser("gen", help="Generate keypair")
    g.add_argument("--bits", type=int, default=512)

    e = sub.add_parser("enc", help="Encrypt")
    e.add_argument("--pub", required=True)
    e.add_argument("msg")

    d = sub.add_parser("dec", help="Decrypt")
    d.add_argument("--priv", required=True)
    d.add_argument("cipher")

    args = parser.parse_args()

    if args.cmd=="gen":
        pub, priv = generate_keypair(args.bits)
        print("Public:", export_public_key_b60(pub))
        print("Private:", export_private_key_b60(priv))

    elif args.cmd=="enc":
        import ast
        pub = import_public_key_b60(ast.literal_eval(args.pub))
        ct = encrypt_b60(args.msg.encode(), pub)
        print("Cipher:", ct)

    elif args.cmd=="dec":
        import ast
        priv = import_private_key_b60(ast.literal_eval(args.priv))
        pt = decrypt_b60(args.cipher, priv)
        print("Plain:", pt.decode(errors="ignore"))

if __name__=="__main__":
    main()
