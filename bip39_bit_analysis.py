def get_bit_pattern_input():
    """Get 4-bit pattern from user input (binary, hex, or decimal)."""
    while True:
        print("\nEnter 4-bit pattern (0-15):")
        print("  Examples: 0000, 1010, 1111 (binary)")
        print("           0, A, F (hex)")
        print("           0, 10, 15 (decimal)")
        
        user_input = input("Pattern: ").strip().upper()
        
        if not user_input:
            continue
            
        try:
            # Try to parse as different formats
            if all(c in '01' for c in user_input) and len(user_input) <= 4:
                # Binary input
                pattern = int(user_input, 2)
            elif all(c in '0123456789ABCDEF' for c in user_input) and len(user_input) <= 1:
                # Hex input (single character)
                pattern = int(user_input, 16)
            else:
                # Decimal input
                pattern = int(user_input, 10)
            
            if 0 <= pattern <= 15:
                return pattern
            else:
                print("Error: Pattern must be between 0 and 15")
                
        except ValueError:
            print("Error: Invalid input format")

def analyze_specific_bit_pattern(target_pattern=None):
    """Find BIP39 words whose indices have specific last 4 bits."""
    
    # Load the BIP39 wordlist
    try:
        with open("english.txt", 'r', encoding='utf-8') as f:
            words = [line.strip() for line in f.readlines()]
        
        if len(words) != 2048:
            print(f"Warning: Expected 2048 words, got {len(words)}")
            return
            
    except FileNotFoundError:
        print("Error: Could not find english.txt")
        print("Please ensure the BIP39 english.txt wordlist is in the same directory.")
        return
    
    # Get target pattern from user if not provided
    if target_pattern is None:
        target_pattern = get_bit_pattern_input()
    
    # Find words with matching last 4 bits
    matching_words = []
    
    for index, word in enumerate(words):
        # Check if last 4 bits match target pattern
        if (index & 0xF) == target_pattern:
            matching_words.append((index, word))
    
    pattern_binary = f"{target_pattern:04b}"
    pattern_hex = f"{target_pattern:X}"
    
    print(f"\nBIP39 Words with Last 4 Bits = {pattern_binary} (hex: {pattern_hex}, decimal: {target_pattern})")
    print("=" * 70)
    print(f"Total words found: {len(matching_words)}")
    print(f"Percentage: {len(matching_words)/2048*100:.1f}%")
    print()
    
    # Show first 20 words, then ask if user wants to see all
    display_limit = 20
    
    print("Index | Binary (11-bit) | Hex  | Word")
    print("-" * 50)
    
    for i, (index, word) in enumerate(matching_words):
        if i >= display_limit:
            show_all = input(f"\nShowing first {display_limit} words. Show all {len(matching_words)} words? (y/n): ").strip().lower()
            if show_all == 'y':
                display_limit = len(matching_words)
                print("Index | Binary (11-bit) | Hex  | Word")
                print("-" * 50)
            else:
                break
        
        binary_11bit = f"{index:011b}"
        hex_value = f"{index:03x}"
        print(f"{index:4d} | {binary_11bit} | {hex_value} | {word}")
    
    print()
    print("Analysis:")
    print(f"• Expected count: 2048 ÷ 16 = {2048//16} words")
    print(f"• Actual count: {len(matching_words)} words")
    print(f"• Last 4 bits pattern: .......{pattern_binary}")
    print()
    
    # Show the mathematical pattern
    start_indices = [target_pattern + i * 16 for i in range(8)]  # Show first 8 examples
    print("Pattern occurs at indices:")
    print(f"• {target_pattern}, {target_pattern + 16}, {target_pattern + 32}, {target_pattern + 48}, {target_pattern + 64}, ...")
    print(f"• Formula: {target_pattern} + (16 × n) where n = 0, 1, 2, 3, ...")
    
    return matching_words

def analyze_all_bit_patterns():
    """Analyze distribution of last 4 bits across all patterns."""
    
    try:
        with open("english.txt", 'r', encoding='utf-8') as f:
            words = [line.strip() for line in f.readlines()]
    except FileNotFoundError:
        print("Error: Could not find english.txt")
        return
    
    # Count words for each last-4-bit pattern
    bit_pattern_counts = {}
    
    for index in range(len(words)):
        last_4_bits = index & 0xF  # Extract last 4 bits
        if last_4_bits not in bit_pattern_counts:
            bit_pattern_counts[last_4_bits] = []
        bit_pattern_counts[last_4_bits].append((index, words[index]))
    
    print("\nDistribution of Last 4 Bits Across All Patterns:")
    print("=" * 60)
    print("Pattern | Count | Example Indices | Example Words")
    print("-" * 60)
    
    for pattern in range(16):  # 0000 to 1111
        pattern_binary = f"{pattern:04b}"
        count = len(bit_pattern_counts.get(pattern, []))
        
        # Get first few examples
        examples = bit_pattern_counts.get(pattern, [])[:3]
        example_indices = [str(idx) for idx, _ in examples]
        example_words = [word for _, word in examples]
        
        print(f"{pattern_binary}  | {count:4d}  | {', '.join(example_indices):<15} | {', '.join(example_words)}")
    
    print()
    print(f"Total words: {sum(len(words_list) for words_list in bit_pattern_counts.values())}")
    print("Each pattern should have exactly 128 words (2048 ÷ 16 = 128)")

def compare_bit_patterns():
    """Compare multiple bit patterns side by side."""
    patterns_to_compare = []
    
    print("\nCompare Multiple Bit Patterns")
    print("Enter patterns to compare (press Enter when done):")
    
    while len(patterns_to_compare) < 8:  # Limit to 8 patterns for readability
        try:
            pattern_input = input(f"Pattern {len(patterns_to_compare) + 1} (or Enter to finish): ").strip()
            if not pattern_input:
                break
            
            # Parse the pattern
            if all(c in '01' for c in pattern_input) and len(pattern_input) <= 4:
                pattern = int(pattern_input, 2)
            elif all(c in '0123456789ABCDEF' for c in pattern_input.upper()) and len(pattern_input) <= 1:
                pattern = int(pattern_input, 16)
            else:
                pattern = int(pattern_input, 10)
            
            if 0 <= pattern <= 15:
                patterns_to_compare.append(pattern)
            else:
                print("Pattern must be between 0 and 15")
                
        except ValueError:
            print("Invalid input format")
    
    if not patterns_to_compare:
        print("No patterns to compare.")
        return
    
    # Load wordlist
    try:
        with open("english.txt", 'r', encoding='utf-8') as f:
            words = [line.strip() for line in f.readlines()]
    except FileNotFoundError:
        print("Error: Could not find english.txt")
        return
    
    print(f"\nComparing {len(patterns_to_compare)} bit patterns:")
    print("=" * 60)
    
    # Header
    header = "Pattern | Binary | Hex | Dec | First 5 Words"
    print(header)
    print("-" * len(header))
    
    for pattern in patterns_to_compare:
        # Find first 5 words with this pattern
        matching_words = []
        for index, word in enumerate(words):
            if (index & 0xF) == pattern:
                matching_words.append(word)
                if len(matching_words) >= 5:
                    break
        
        pattern_binary = f"{pattern:04b}"
        pattern_hex = f"{pattern:X}"
        first_words = ', '.join(matching_words[:5])
        
        print(f"{pattern_binary}    | {pattern_binary} | {pattern_hex}   | {pattern:2d}  | {first_words}")

def interactive_bit_explorer():
    """Interactive exploration of bit patterns."""
    try:
        with open("english.txt", 'r', encoding='utf-8') as f:
            words = [line.strip() for line in f.readlines()]
    except FileNotFoundError:
        print("Error: Could not find english.txt")
        return
    
    print("\nInteractive Bit Pattern Explorer")
    print("=" * 40)
    print("Enter a word to see its bit pattern, or a pattern to see words")
    print("Type 'quit' to exit")
    
    while True:
        user_input = input("\nEnter word or bit pattern: ").strip().lower()
        
        if user_input == 'quit':
            break
            
        if not user_input:
            continue
        
        # Check if input is a word
        if user_input in words:
            index = words.index(user_input)
            binary_11bit = f"{index:011b}"
            last_4_bits = index & 0xF
            last_4_binary = f"{last_4_bits:04b}"
            
            print(f"\nWord: '{user_input}'")
            print(f"Index: {index}")
            print(f"Full binary (11-bit): {binary_11bit}")
            print(f"Last 4 bits: {last_4_binary} (decimal: {last_4_bits}, hex: {last_4_bits:X})")
            
            # Show other words with same last 4 bits
            same_pattern_words = []
            for i, w in enumerate(words):
                if (i & 0xF) == last_4_bits and w != user_input:
                    same_pattern_words.append(w)
                    if len(same_pattern_words) >= 5:
                        break
            
            if same_pattern_words:
                print(f"Other words with same last 4 bits: {', '.join(same_pattern_words)}")
        
        else:
            # Try to parse as bit pattern
            try:
                if all(c in '01' for c in user_input) and len(user_input) <= 4:
                    pattern = int(user_input, 2)
                elif all(c in '0123456789abcdef' for c in user_input) and len(user_input) <= 1:
                    pattern = int(user_input, 16)
                else:
                    pattern = int(user_input, 10)
                
                if 0 <= pattern <= 15:
                    # Show words with this pattern
                    matching_words = []
                    for index, word in enumerate(words):
                        if (index & 0xF) == pattern:
                            matching_words.append((index, word))
                            if len(matching_words) >= 10:
                                break
                    
                    pattern_binary = f"{pattern:04b}"
                    print(f"\nBit pattern: {pattern_binary} (decimal: {pattern}, hex: {pattern:X})")
                    print("First 10 matching words:")
                    for index, word in matching_words:
                        print(f"  {word} (index: {index})")
                else:
                    print("Pattern must be between 0 and 15")
                    
            except ValueError:
                print(f"'{user_input}' not found in wordlist and not a valid bit pattern")

def main():
    print("BIP39 Bit Pattern Analysis Tool")
    print("=" * 45)
    print("1. Find words with specific last 4 bits")
    print("2. Show all bit pattern distributions")
    print("3. Compare multiple bit patterns")
    print("4. Interactive bit pattern explorer")
    print("5. Quick analysis (0000 pattern)")
    print("6. Quit")
    
    while True:
        choice = input("\nEnter your choice (1-6): ").strip()
        
        if choice == '1':
            analyze_specific_bit_pattern()
        elif choice == '2':
            analyze_all_bit_patterns()
        elif choice == '3':
            compare_bit_patterns()
        elif choice == '4':
            interactive_bit_explorer()
        elif choice == '5':
            analyze_specific_bit_pattern(0)  # Quick 0000 analysis
        elif choice == '6':
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()