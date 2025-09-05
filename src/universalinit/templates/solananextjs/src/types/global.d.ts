declare namespace NodeJS {
  interface ProcessEnv {
    NEXT_PUBLIC_SOLANA_RPC_URL: string;
    NEXT_PUBLIC_SOLANA_WS_URL: string;
  }
}

interface Window {
  solana?: {
    isPhantom?: boolean;
    connect(): Promise<{ publicKey: { toBase58(): string; toString(): string } }>;
    disconnect(): Promise<void>;
    signMessage?(message: Uint8Array, encoding: string): Promise<Uint8Array | { signature: Uint8Array }>;
    signTransaction?(transaction: import("@solana/web3.js").Transaction): Promise<import("@solana/web3.js").Transaction>;
    publicKey?: {
      toBase58?(): string;
      toString?(): string;
    };
  };
}
