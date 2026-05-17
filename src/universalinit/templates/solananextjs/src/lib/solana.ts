"use client";

import nacl from "tweetnacl";
import bs58 from "bs58";
import { 
  Connection, 
  PublicKey, 
  Transaction, 
  TransactionInstruction 
} from "@solana/web3.js";

// Default to localnet if environment variables are not set
const rpcUrl = process.env.NEXT_PUBLIC_SOLANA_RPC_URL || "http://localhost:8899";
const wsUrl = process.env.NEXT_PUBLIC_SOLANA_WS_URL || "ws://localhost:8900";

// Create a singleton connection instance
export const connection = new Connection(rpcUrl, {
  wsEndpoint: wsUrl,
  commitment: "confirmed"
});

/** Phantom-like provider detection. */
// PUBLIC_INTERFACE
export function getProvider(): Window["solana"] | null {
  /** Return the injected Solana provider if present (e.g., Phantom). */
  if (typeof window === "undefined") return null;
  const anyWindow = window as Window;
  if (anyWindow?.solana?.isPhantom || anyWindow?.solana) {
    return anyWindow.solana!;
  }
  return null;
}

// PUBLIC_INTERFACE
export async function connectWallet(): Promise<string> {
  /** Connect to the wallet and return the base58 public key. */
  const provider = getProvider();
  if (!provider) throw new Error("No Solana wallet found. Install Phantom or a compatible wallet.");
  const res = await provider.connect();
  const pk = res?.publicKey?.toBase58?.() ?? res?.publicKey?.toString?.();
  if (!pk) throw new Error("Failed to read wallet public key.");
  return pk;
}

// PUBLIC_INTERFACE
export async function disconnectWallet(): Promise<void> {
  /** Disconnect the current wallet if connected. */
  const provider = getProvider();
  if (!provider) return;
  try {
    await provider.disconnect();
  } catch {
    // ignore
  }
}

// PUBLIC_INTERFACE
export async function signMessage(message: string): Promise<{
  signature: string;
  publicKey: string;
}> {
  /** Request the wallet to sign an arbitrary message. Returns base58 signature and public key. */
  const provider = getProvider();
  if (!provider) throw new Error("No wallet available to sign.");

  const encoder = new TextEncoder();
  const msgBytes = encoder.encode(message);

  if (!provider.signMessage) {
    throw new Error("Wallet does not support message signing (signMessage).");
  }
  const res = await provider.signMessage(msgBytes, "utf8");
  const sigBytes = ArrayBuffer.isView(res)
    ? (res as Uint8Array)
    : (res as { signature: Uint8Array }).signature;

  const pk = provider.publicKey?.toBase58?.() ?? provider.publicKey?.toString?.();
  if (!pk) {
    throw new Error("Unable to read wallet public key.");
  }
  return {
    signature: bs58.encode(sigBytes),
    publicKey: pk,
  };
}

// PUBLIC_INTERFACE
export function verifySignature(message: string, signatureB58: string, publicKeyB58: string): boolean {
  /** Verify a base58-encoded signature for the given message using the base58 public key. */
  const encoder = new TextEncoder();
  const msgBytes = encoder.encode(message);
  const sigBytes = bs58.decode(signatureB58);
  const pubKeyBytes = bs58.decode(publicKeyB58);
  return nacl.sign.detached.verify(msgBytes, sigBytes, pubKeyBytes);
}

// PUBLIC_INTERFACE
export async function submitMemoTransaction(message: string): Promise<string> {
  /** Submit a memo transaction to the Solana blockchain with the given message. */
  const provider = getProvider();
  if (!provider) throw new Error("No wallet available.");
  if (!provider.publicKey) throw new Error("Wallet not connected.");

  // Use the configured connection (defaults to localnet if not configured)
  const connection = new Connection(rpcUrl);

  // Create memo program instruction
  const MEMO_PROGRAM_ID = new PublicKey("MemoSq4gqABAXKb96qnH8TysNcWxMyWCqXgDLGmfcHr");
  const instruction = new TransactionInstruction({
    keys: [],
    programId: MEMO_PROGRAM_ID,
    data: Buffer.from(message),
  });

  // Create transaction
  const transaction = new Transaction().add(instruction);
  if (!provider.publicKey) throw new Error("Wallet not connected");
  const publicKeyStr = provider.publicKey?.toBase58?.() ?? provider.publicKey?.toString?.();
  if (!publicKeyStr) throw new Error("Unable to read wallet public key");
  transaction.feePayer = new PublicKey(publicKeyStr);
  
  try {
    // Get recent blockhash
    const { blockhash } = await connection.getLatestBlockhash();
    transaction.recentBlockhash = blockhash;

    // Request signature from wallet
    if (!provider.signTransaction) {
      throw new Error("Wallet does not support transaction signing");
    }
    const signedTransaction = await provider.signTransaction(transaction);
    
    // Send transaction
    const signature = await connection.sendRawTransaction(signedTransaction.serialize());
    
    // Confirm transaction
    await connection.confirmTransaction(signature);
    
    return signature;
  } catch (error: unknown) {
    console.error("Failed to submit memo transaction:", error);
    
    // Check for insufficient balance error
    const errorMessage = error instanceof Error ? error.message : String(error);
    if (errorMessage.includes("Attempt to debit an account but found no record of a prior credit")) {
      // Developer note: For development, fund the wallet using:
      // solana airdrop 1 <WALLET_ADDRESS> --url http://localhost:8899
      console.warn(
        "Developer Note: Local wallet needs SOL. Use 'solana airdrop' command to fund the wallet for development."
      );
      
      throw new Error(
        "Insufficient SOL balance in wallet. Please ensure your wallet has SOL tokens before signing transactions."
      );
    }
    
    // Handle other transaction errors
    throw new Error(
      `Failed to submit prescription to blockchain: ${errorMessage}`
    );
  }
}
