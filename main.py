import hashlib
import secrets


class BIP39Generator:
    def __init__(self, wordlist_file="english.txt"):
        """Initialize the BIP39 generator with the wordlist."""
        self.wordlist = self.load_wordlist(wordlist_file)
        
    def load_wordlist(self, filename):
        """Load the BIP39 wordlist from file."""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                words = [line.strip() for line in f.readlines()]
            
            if len(words) != 2048:
                raise ValueError(f"Expected 2048 words, got {len(words)}")
            
            return words
        except FileNotFoundError:
            print(f"Error: Could not find {filename}")
            print("Please ensure the BIP39 english.txt wordlist is in the same directory.")
            return None
        except Exception as e:
            print(f"Error loading wordlist: {e}")
            return None
    
    def generate_random_entropy(self):
        """Generate 128 bits (16 bytes) of cryptographically secure random entropy."""
        return secrets.randbits(128)
    
    def entropy_from_hex(self, hex_string):
        """Convert hex string to 128-bit integer."""
        try:
            # Remove any whitespace and 0x prefix if present
            hex_string = hex_string.strip().replace('0x', '')
            
            if len(hex_string) != 32:
                raise ValueError("Hex string must be exactly 32 characters (128 bits)")
            
            return int(hex_string, 16)
        except ValueError as e:
            raise ValueError(f"Invalid hex input: {e}")
    
    def entropy_from_binary(self, binary_string):
        """Convert binary string to 128-bit integer."""
        try:
            # Remove any whitespace
            binary_string = binary_string.strip().replace(' ', '')
            
            if len(binary_string) != 128:
                raise ValueError("Binary string must be exactly 128 characters")
            
            if not all(c in '01' for c in binary_string):
                raise ValueError("Binary string can only contain 0s and 1s")
            
            return int(binary_string, 2)
        except ValueError as e:
            raise ValueError(f"Invalid binary input: {e}")
    
    def calculate_checksum(self, entropy_bits):
        """Calculate the 4-bit checksum for 128-bit entropy."""
        # Convert entropy to bytes (16 bytes for 128 bits)
        entropy_bytes = entropy_bits.to_bytes(16, byteorder='big')
        
        # Calculate SHA256 hash
        hash_result = hashlib.sha256(entropy_bytes).digest()
        
        # Take first byte of hash and extract first 4 bits
        checksum = hash_result[0] >> 4
        
        return checksum
    
    def bits_to_mnemonic(self, entropy_bits):
        """Convert 128-bit entropy to 12-word mnemonic."""
        if not self.wordlist:
            return None
        
        # Calculate checksum
        checksum = self.calculate_checksum(entropy_bits)
        
        # Combine entropy (128 bits) + checksum (4 bits) = 132 bits
        combined_bits = (entropy_bits << 4) | checksum
        
        # Split into 12 groups of 11 bits
        words = []
        for i in range(12):
            # Extract 11 bits starting from the most significant bit
            word_index = (combined_bits >> (121 - i * 11)) & 0x7FF  # 0x7FF = 2047 = 11 bits set
            words.append(self.wordlist[word_index])
        
        return words
    
    def generate_mnemonic(self, entropy_input=None, input_type='random'):
        """
        Generate a BIP39 mnemonic phrase.
        
        Args:
            entropy_input: User-provided entropy (hex string, binary string, or None for random)
            input_type: 'random', 'hex', or 'binary'
        
        Returns:
            List of 12 words or None if error
        """
        try:
            if input_type == 'random' or entropy_input is None:
                entropy_bits = self.generate_random_entropy()
            elif input_type == 'hex':
                entropy_bits = self.entropy_from_hex(entropy_input)
            elif input_type == 'binary':
                entropy_bits = self.entropy_from_binary(entropy_input)
            else:
                raise ValueError("Invalid input type. Use 'random', 'hex', or 'binary'")
            
            return self.bits_to_mnemonic(entropy_bits)
            
        except ValueError as e:
            print(f"Error: {e}")
            return None
    
    def display_detailed_info(self, entropy_input=None, input_type='random'):
        """Display detailed information about the mnemonic generation process."""
        try:
            if input_type == 'random' or entropy_input is None:
                entropy_bits = self.generate_random_entropy()
                print("Generated random 128-bit entropy")
            elif input_type == 'hex':
                entropy_bits = self.entropy_from_hex(entropy_input)
                print(f"Using provided hex entropy: {entropy_input}")
            elif input_type == 'binary':
                entropy_bits = self.entropy_from_binary(entropy_input)
                print(f"Using provided binary entropy")
            
            checksum = self.calculate_checksum(entropy_bits)
            combined_bits = (entropy_bits << 4) | checksum
            
            print(f"\nEntropy (128 bits): {entropy_bits:032x}")
            print(f"Entropy (binary):   {entropy_bits:0128b}")
            print(f"Checksum (4 bits):  {checksum:04b}")
            print(f"Combined (132 bits): {combined_bits:033x}")
            
            words = self.bits_to_mnemonic(entropy_bits)
            if words:
                print(f"\nMnemonic phrase:")
                for i, word in enumerate(words, 1):
                    word_index = self.wordlist.index(word)
                    word_bits = (combined_bits >> (121 - (i-1) * 11)) & 0x7FF
                    print(f"{i:2d}. {word:<12} (index: {word_index:4d}, bits: {word_bits:011b})")
                
                print(f"\nComplete mnemonic: {' '.join(words)}")
            
        except Exception as e:
            print(f"Error: {e}")

def main():
    # Initialize the generator
    generator = BIP39Generator()
    
    if not generator.wordlist:
        return
    
    while True:
        print("\n" + "="*60)
        print("BIP39 Mnemonic Generator")
        print("="*60)
        print("1. Generate random mnemonic")
        print("2. Generate from hex entropy (32 hex characters)")
        print("3. Generate from binary entropy (128 binary digits)")
        print("4. Show detailed generation info")
        print("5. Quit")
        
        choice = input("\nEnter your choice (1-5): ").strip()
        
        if choice == '1':
            words = generator.generate_mnemonic()
            if words:
                print(f"\nGenerated mnemonic: {' '.join(words)}")
        
        elif choice == '2':
            hex_input = input("Enter 128-bit entropy as hex (32 characters): ").strip()
            words = generator.generate_mnemonic(hex_input, 'hex')
            if words:
                print(f"\nGenerated mnemonic: {' '.join(words)}")
        
        elif choice == '3':
            binary_input = input("Enter 128-bit entropy as binary (128 digits): ").strip()
            words = generator.generate_mnemonic(binary_input, 'binary')
            if words:
                print(f"\nGenerated mnemonic: {' '.join(words)}")
        
        elif choice == '4':
            print("\nDetailed generation info:")
            print("1. Random entropy")
            print("2. From hex entropy")
            print("3. From binary entropy")
            
            detail_choice = input("Choose option (1-3): ").strip()
            
            if detail_choice == '1':
                generator.display_detailed_info()
            elif detail_choice == '2':
                hex_input = input("Enter 128-bit entropy as hex: ").strip()
                generator.display_detailed_info(hex_input, 'hex')
            elif detail_choice == '3':
                binary_input = input("Enter 128-bit entropy as binary: ").strip()
                generator.display_detailed_info(binary_input, 'binary')
        
        elif choice == '5':
            print("Goodbye!")
            break
        
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()