import hashlib

class BIP39Validator:
    def __init__(self, wordlist_file="english.txt"):
        """Initialize the BIP39 validator with the wordlist."""
        self.wordlist = self.load_wordlist(wordlist_file)
        # Create a set for O(1) word lookups
        self.wordset = set(self.wordlist) if self.wordlist else None
        
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
    
    def validate_word_count(self, mnemonic_words):
        """Validate that the mnemonic has the correct number of words."""
        valid_lengths = {12: 128, 15: 160, 18: 192, 21: 224, 24: 256}
        word_count = len(mnemonic_words)
        
        if word_count not in valid_lengths:
            return False, f"Invalid word count: {word_count}. Valid counts are: {list(valid_lengths.keys())}"
        
        return True, valid_lengths[word_count]
    
    def validate_words_in_wordlist(self, mnemonic_words):
        """Check if all words are in the BIP39 wordlist."""
        if not self.wordset:
            return False, "Wordlist not loaded"
        
        invalid_words = []
        for i, word in enumerate(mnemonic_words):
            if word not in self.wordset:
                invalid_words.append((i + 1, word))
        
        if invalid_words:
            error_msg = "Invalid words found:\n"
            for pos, word in invalid_words:
                error_msg += f"  Position {pos}: '{word}'\n"
            return False, error_msg.strip()
        
        return True, "All words are in the BIP39 wordlist"
    
    def calculate_checksum_bits(self, entropy_bits, entropy_bit_length):
        """Calculate the expected checksum bits."""
        # Convert entropy to bytes
        entropy_byte_length = entropy_bit_length // 8
        entropy_bytes = entropy_bits.to_bytes(entropy_byte_length, byteorder='big')
        
        # Calculate SHA256 hash
        hash_result = hashlib.sha256(entropy_bytes).digest()
        
        # Extract checksum bits (entropy_bit_length / 32 bits from the hash)
        checksum_bit_length = entropy_bit_length // 32
        
        # Extract the required number of bits from the first byte(s) of the hash
        checksum = 0
        for i in range(checksum_bit_length):
            bit_index = i
            byte_index = bit_index // 8
            bit_in_byte = 7 - (bit_index % 8)
            bit_value = (hash_result[byte_index] >> bit_in_byte) & 1
            checksum = (checksum << 1) | bit_value
        
        return checksum
    
    def validate_checksum(self, mnemonic_words, entropy_bit_length):
        """Validate the checksum of the mnemonic."""
        # Convert words to indices
        word_indices = []
        for word in mnemonic_words:
            try:
                index = self.wordlist.index(word)
                word_indices.append(index)
            except ValueError:
                return False, f"Word '{word}' not found in wordlist"
        
        # Convert indices to bits
        total_bits = len(mnemonic_words) * 11
        combined_bits = 0
        
        for index in word_indices:
            combined_bits = (combined_bits << 11) | index
        
        # Calculate checksum length
        checksum_bit_length = entropy_bit_length // 32
        
        # Split entropy and checksum
        entropy_bits = combined_bits >> checksum_bit_length
        actual_checksum = combined_bits & ((1 << checksum_bit_length) - 1)
        
        # Calculate expected checksum
        expected_checksum = self.calculate_checksum_bits(entropy_bits, entropy_bit_length)
        
        if actual_checksum == expected_checksum:
            return True, f"Checksum valid (expected: {expected_checksum:0{checksum_bit_length}b}, actual: {actual_checksum:0{checksum_bit_length}b})"
        else:
            return False, f"Checksum invalid (expected: {expected_checksum:0{checksum_bit_length}b}, actual: {actual_checksum:0{checksum_bit_length}b})"
    
    def validate_mnemonic(self, mnemonic):
        """
        Validate a BIP39 mnemonic phrase.
        
        Args:
            mnemonic: Space-separated string of mnemonic words
        
        Returns:
            tuple: (is_valid, details_dict)
        """
        if not self.wordlist:
            return False, {"error": "Wordlist not loaded"}
        
        # Clean and split the mnemonic
        mnemonic = mnemonic.strip().lower()
        mnemonic_words = mnemonic.split()
        
        results = {
            "mnemonic": mnemonic,
            "word_count": len(mnemonic_words),
            "words": mnemonic_words,
            "validations": {}
        }
        
        # Step 1: Validate word count
        word_count_valid, entropy_bit_length_or_error = self.validate_word_count(mnemonic_words)
        results["validations"]["word_count"] = {
            "valid": word_count_valid,
            "message": entropy_bit_length_or_error if not word_count_valid else f"Valid word count for {entropy_bit_length_or_error}-bit entropy"
        }
        
        if not word_count_valid:
            results["valid"] = False
            return False, results
        
        entropy_bit_length = entropy_bit_length_or_error
        
        # Step 2: Validate words are in wordlist
        words_valid, words_message = self.validate_words_in_wordlist(mnemonic_words)
        results["validations"]["words_in_wordlist"] = {
            "valid": words_valid,
            "message": words_message
        }
        
        if not words_valid:
            results["valid"] = False
            return False, results
        
        # Step 3: Validate checksum
        checksum_valid, checksum_message = self.validate_checksum(mnemonic_words, entropy_bit_length)
        results["validations"]["checksum"] = {
            "valid": checksum_valid,
            "message": checksum_message
        }
        
        # Overall result
        results["valid"] = word_count_valid and words_valid and checksum_valid
        results["entropy_bits"] = entropy_bit_length
        
        return results["valid"], results
    
    def get_mnemonic_info(self, mnemonic):
        """Get detailed information about a mnemonic (valid or invalid)."""
        is_valid, details = self.validate_mnemonic(mnemonic)
        
        if not is_valid:
            return details
        
        # Add extra information for valid mnemonics
        mnemonic_words = details["words"]
        
        # Convert to binary representation
        word_indices = [self.wordlist.index(word) for word in mnemonic_words]
        combined_bits = 0
        for index in word_indices:
            combined_bits = (combined_bits << 11) | index
        
        entropy_bit_length = details["entropy_bits"]
        checksum_bit_length = entropy_bit_length // 32
        
        entropy_bits = combined_bits >> checksum_bit_length
        checksum_bits = combined_bits & ((1 << checksum_bit_length) - 1)
        
        details["binary_info"] = {
            "entropy_binary": f"{entropy_bits:0{entropy_bit_length}b}",
            "entropy_hex": f"{entropy_bits:0{entropy_bit_length//4}x}",
            "checksum_binary": f"{checksum_bits:0{checksum_bit_length}b}",
            "combined_bits": combined_bits,
            "word_indices": word_indices
        }
        
        return details

def main():
    # Initialize the validator
    validator = BIP39Validator()
    
    if not validator.wordlist:
        return
    
    while True:
        print("\n" + "="*60)
        print("BIP39 Mnemonic Validator")
        print("="*60)
        print("1. Validate mnemonic phrase")
        print("2. Show detailed mnemonic information")
        print("3. Test with example mnemonics")
        print("4. Quit")
        
        choice = input("\nEnter your choice (1-4): ").strip()
        
        if choice == '1':
            mnemonic = input("\nEnter mnemonic phrase: ").strip()
            if not mnemonic:
                print("Please enter a mnemonic phrase.")
                continue
            
            is_valid, details = validator.validate_mnemonic(mnemonic)
            
            print(f"\nMnemonic: {details['mnemonic']}")
            print(f"Word Count: {details['word_count']}")
            print(f"Overall Valid: {'✓ YES' if is_valid else '✗ NO'}")
            print("\nValidation Details:")
            
            for check_name, check_result in details['validations'].items():
                status = "✓ PASS" if check_result['valid'] else "✗ FAIL"
                print(f"  {check_name.replace('_', ' ').title()}: {status}")
                print(f"    {check_result['message']}")
        
        elif choice == '2':
            mnemonic = input("\nEnter mnemonic phrase: ").strip()
            if not mnemonic:
                print("Please enter a mnemonic phrase.")
                continue
            
            details = validator.get_mnemonic_info(mnemonic)
            
            print(f"\nDetailed Information:")
            print(f"Mnemonic: {details['mnemonic']}")
            print(f"Word Count: {details['word_count']}")
            print(f"Valid: {'✓ YES' if details['valid'] else '✗ NO'}")
            
            if details['valid']:
                print(f"Entropy Bits: {details['entropy_bits']}")
                binary_info = details['binary_info']
                print(f"Entropy (hex): {binary_info['entropy_hex']}")
                print(f"Entropy (binary): {binary_info['entropy_binary']}")
                print(f"Checksum (binary): {binary_info['checksum_binary']}")
                
                print("\nWord Breakdown:")
                for i, (word, index) in enumerate(zip(details['words'], binary_info['word_indices'])):
                    print(f"  {i+1:2d}. {word:<12} (index: {index:4d}, binary: {index:011b})")
            else:
                print("\nValidation Errors:")
                for check_name, check_result in details['validations'].items():
                    if not check_result['valid']:
                        print(f"  {check_name.replace('_', ' ').title()}: {check_result['message']}")
        
        elif choice == '3':
            # Test with some example mnemonics
            test_mnemonics = [
                "abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon about",  # Valid 12-word
                "abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon",  # Invalid checksum
                "invalid word list test invalid word list test invalid word list",  # Invalid words
                "abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon",  # Wrong word count
            ]
            
            print("\nTesting example mnemonics:")
            for i, test_mnemonic in enumerate(test_mnemonics, 1):
                print(f"\n{i}. Testing: {test_mnemonic}")
                is_valid, details = validator.validate_mnemonic(test_mnemonic)
                print(f"   Result: {'✓ VALID' if is_valid else '✗ INVALID'}")
                if not is_valid:
                    for check_name, check_result in details['validations'].items():
                        if not check_result['valid']:
                            print(f"   Issue: {check_result['message']}")
                            break
        
        elif choice == '4':
            print("Goodbye!")
            break
        
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()