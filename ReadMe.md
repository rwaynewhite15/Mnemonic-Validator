# BIP39 Mnemonic Generator - Line by Line Explanation

## Import Statements (Lines 1-3)

```python
import hashlib
import secrets
```

- **Line 1**: `hashlib` - Python's built-in library for cryptographic hash functions. We use it for SHA256 to calculate the checksum
- **Line 2**: `secrets` - Python's cryptographically secure random number generator. More secure than `random` for cryptographic purposes

## Class Definition and Initialization (Lines 5-9)

```python
class BIP39Generator:
    def __init__(self, wordlist_file="english.txt"):
        """Initialize the BIP39 generator with the wordlist."""
        self.wordlist = self.load_wordlist(wordlist_file)
```

- **Line 5**: Define the main class that will contain all our BIP39 functionality
- **Line 6**: Constructor method that runs when creating a new instance. Takes optional `wordlist_file` parameter (defaults to "english.txt")
- **Line 7**: Docstring explaining what this method does
- **Line 8**: Calls `load_wordlist()` method and stores the result in `self.wordlist` instance variable

## Loading the Wordlist (Lines 10-26)

```python
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
```

- **Line 10**: Method definition to load wordlist from file
- **Line 12**: Start try block for error handling
- **Line 13**: Open file with UTF-8 encoding (handles special characters properly)
- **Line 14**: List comprehension that reads all lines, strips whitespace from each line, creates list of words
- **Line 16-17**: Validate that we have exactly 2048 words (BIP39 requirement). If not, raise error
- **Line 19**: Return the list of words if successful
- **Line 20-23**: Handle case where file doesn't exist, print helpful error message, return None
- **Line 24-26**: Handle any other errors, print error message, return None

## Random Entropy Generation (Lines 28-31)

```python
def generate_random_entropy(self):
    """Generate 128 bits (16 bytes) of cryptographically secure random entropy."""
    return secrets.randbits(128)
```

- **Line 28**: Method to generate random entropy
- **Line 30**: Use `secrets.randbits(128)` to generate exactly 128 random bits. Returns integer

## Hex Input Processing (Lines 33-47)

```python
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
```

- **Line 33**: Method to convert hex string to integer
- **Line 35**: Start try block
- **Line 37**: Clean the input - remove whitespace and optional "0x" prefix
- **Line 39-40**: Validate length - 32 hex characters = 128 bits (each hex char = 4 bits)
- **Line 42**: Convert hex string to integer using base 16
- **Line 43-44**: Re-raise any ValueError with more descriptive message

## Binary Input Processing (Lines 49-66)

```python
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
```

- **Line 49**: Method to convert binary string to integer
- **Line 52**: Clean input by removing whitespace and spaces
- **Line 54-55**: Validate length is exactly 128 characters
- **Line 57-58**: Validate that string only contains '0' and '1'. `all()` returns True if all characters pass the test
- **Line 60**: Convert binary string to integer using base 2
- **Line 61-62**: Re-raise ValueError with descriptive message

## Checksum Calculation (Lines 68-79)

```python
def calculate_checksum(self, entropy_bits):
    """Calculate the 4-bit checksum for 128-bit entropy."""
    # Convert entropy to bytes (16 bytes for 128 bits)
    entropy_bytes = entropy_bits.to_bytes(16, byteorder='big')
    
    # Calculate SHA256 hash
    hash_result = hashlib.sha256(entropy_bytes).digest()
    
    # Take first byte of hash and extract first 4 bits
    checksum = hash_result[0] >> 4
    
    return checksum
```

- **Line 68**: Method to calculate BIP39 checksum
- **Line 71**: Convert integer to 16 bytes (128 bits ÷ 8 = 16 bytes) in big-endian format
- **Line 74**: Calculate SHA256 hash of the entropy bytes, `.digest()` returns raw bytes
- **Line 77**: Take first byte of hash (`hash_result[0]`) and right-shift by 4 bits to get top 4 bits
- **Line 79**: Return the 4-bit checksum

## Converting Bits to Mnemonic (Lines 81-100)

```python
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
```

- **Line 81**: Method to convert entropy bits to mnemonic words
- **Line 83-84**: Check if wordlist loaded successfully, return None if not
- **Line 87**: Calculate the 4-bit checksum
- **Line 90**: Combine entropy and checksum: shift entropy left 4 bits, then OR with checksum
- **Line 93-94**: Initialize empty list for words, start loop for 12 words
- **Line 96**: Extract 11 bits for each word:
  - `121 - i * 11`: Starting position (121, 110, 99, 88, 77, 66, 55, 44, 33, 22, 11, 0)
  - `combined_bits >> (121 - i * 11)`: Right-shift to bring desired bits to rightmost position
  - `& 0x7FF`: Mask with 0x7FF (binary: 11111111111) to keep only bottom 11 bits
- **Line 97**: Use the 11-bit value as index into wordlist, add word to list
- **Line 99**: Return list of 12 words

## Main Generation Method (Lines 102-127)

```python
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
```

- **Line 102**: Main method that orchestrates mnemonic generation
- **Line 112-113**: If random or no input provided, generate random entropy
- **Line 114-115**: If hex input, convert hex to entropy bits
- **Line 116-117**: If binary input, convert binary to entropy bits
- **Line 118-119**: If invalid input type, raise error
- **Line 121**: Convert entropy bits to mnemonic and return
- **Line 123-125**: Handle any errors, print message, return None

## Detailed Information Display (Lines 129-162)

```python
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
```

- **Line 129**: Method for showing detailed generation process
- **Line 131-139**: Handle different input types, same logic as `generate_mnemonic()` but with print statements
- **Line 141-142**: Calculate checksum and combine with entropy
- **Line 144**: Print entropy as 32-digit hex (`:032x` means 32 digits, zero-padded, hexadecimal)
- **Line 145**: Print entropy as 128-digit binary (`:0128b` means 128 digits, zero-padded, binary)
- **Line 146**: Print checksum as 4-digit binary (`:04b`)
- **Line 147**: Print combined bits as 33-digit hex (`:033x`)
- **Line 149-150**: Generate mnemonic words
- **Line 152**: Start detailed word breakdown
- **Line 153**: Loop through words with index starting at 1
- **Line 154**: Find word's index in wordlist
- **Line 155**: Extract the 11 bits that correspond to this word (same logic as in `bits_to_mnemonic`)
- **Line 156**: Print formatted info: word number, word (left-aligned in 12 chars), wordlist index, and 11-bit binary
- **Line 158**: Print complete mnemonic phrase

## Main Function - User Interface (Lines 164-220)

```python
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
```

- **Line 164**: Main function that runs the program
- **Line 166**: Create instance of BIP39Generator class
- **Line 168-169**: Exit if wordlist failed to load
- **Line 171**: Start infinite loop for menu
- **Line 172-179**: Print menu header and options
- **Line 181**: Get user input, strip whitespace

## Menu Option Handling (Lines 183-220)

```python
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
```

- **Line 183-186**: Handle option 1 - generate random mnemonic and print if successful
- **Line 188-192**: Handle option 2 - get hex input, generate mnemonic, print if successful
- **Line 194-198**: Handle option 3 - get binary input, generate mnemonic, print if successful
- **Line 200-213**: Handle option 4 - detailed info submenu with three sub-options
- **Line 215-217**: Handle option 5 - exit program by breaking the loop
- **Line 219-220**: Handle invalid menu choices

## Program Entry Point (Lines 222-223)

```python
if __name__ == "__main__":
    main()
```

- **Line 222**: Python idiom - only run `main()` if this file is executed directly (not imported)
- **Line 223**: Call the main function to start the program

## Key Concepts Explained:

1. **Bit Shifting (`<<`, `>>`)**: Moving bits left or right. `x << 4` moves all bits 4 positions left (multiplies by 16)

2. **Bitwise OR (`|`)**: Combines bits. `1010 | 0101 = 1111`

3. **Bitwise AND (`&`)**: Masks bits. `1111 & 0101 = 0101`

4. **Format Strings**: `{value:032x}` means format as hex with 32 digits, zero-padded

5. **BIP39 Process**: 128 bits entropy + 4 bits checksum = 132 bits ÷ 11 bits per word = 12 words