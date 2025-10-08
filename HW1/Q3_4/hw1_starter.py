#!/usr/bin/env python

### hw1_starter.py

import sys
from BitVector import *
from get_encryption_key import get_encryption_key
from generate_round_keys import generate_round_keys
from illustrate_des_substitution import substitute
import illustrate_des_substitution
from copy import deepcopy
import random
from tqdm import tqdm
from scipy.stats import ttest_ind
from statistics import mean

expansion_permutation = [31, 0, 1, 2, 3, 4, 3, 4, 5, 6, 7, 8, 7, 8, 9, 10, 11, 12, 11, 12, 13, 14, 15, 16, 15, 16, 17, 18, 19, 20, 19, 20, 21, 22, 23, 24, 23, 24, 25, 26, 27, 28, 27, 28, 29, 30, 31, 0]

p_box_permutation = [15, 6, 19, 20, 28, 11, 27, 16, 0, 14, 22, 25, 4, 17, 30, 9, 1, 7, 23, 13, 31, 26, 2, 8, 18, 12, 29, 5, 21, 10, 3, 24]

init_permutation = [57, 49, 41, 33, 25, 17, 9, 1, 59, 51, 43, 35, 27, 19, 11, 3, 61, 53, 45, 37, 29, 21, 13, 5, 63, 55, 47, 39, 31, 23, 15, 7, 56, 48, 40, 32, 24, 16, 8, 0, 58, 50, 42, 34, 26, 18, 10, 2, 60, 52, 44, 36, 28, 20, 12, 4, 62, 54, 46, 38, 30, 22, 14, 6]

final_permutation = [39, 7, 47, 15, 55, 23, 63, 31, 38, 6, 46, 14, 54, 22, 62, 30, 37, 5, 45, 13, 53, 21, 61, 29, 36, 4, 44, 12, 52, 20, 60, 28, 35, 3, 43, 11, 51, 19, 59, 27, 34, 2, 42, 10, 50, 18, 58, 26, 33, 1, 41, 9, 49, 17, 57, 25, 32, 0, 40, 8, 48, 16, 56, 24]

ORIGINAL_S_BOX = deepcopy(illustrate_des_substitution.s_boxes)

def DES_block(LE, RE, round_key):
    eRE = RE.permute( expansion_permutation )
    out_xor = eRE ^ round_key
    out_s = substitute( out_xor )
    out_p = out_s.permute( p_box_permutation )
    new_RE = out_p ^ LE
    return (RE, new_RE)

def DES(bitvec, round_keys):
    if bitvec._getsize() < 64:
        bitvec.pad_from_right(64 - bitvec._getsize())
    bitvec = bitvec.permute( init_permutation )
    [LE, RE] = bitvec.divide_into_two()
    for round_key in round_keys:
        (LE, RE) = DES_block( LE, RE, round_key )
    final_string = RE + LE
    final_string = final_string.permute( final_permutation )
    return final_string

def encrypt():
    key = get_encryption_key()
    round_keys = generate_round_keys( key )
    bv = BitVector( filename='filename.txt' )
    while (bv.more_to_read):
        bitvec = bv.read_bits_from_file( 64 )
        final_string = DES( bitvec, round_keys )
        with open('output.txt.enc', 'ab') as f:
            final_string.write_to_file( f )

def decode():
    key = get_encryption_key()
    round_keys = generate_round_keys( key )[::-1]
    bv = BitVector( filename='output.txt.enc' )
    while (bv.more_to_read):
        bitvec = bv.read_bits_from_file( 64 )
        final_string = DES( bitvec, round_keys )
        with open('output.txt', 'ab') as f:
            final_string.write_to_file( f )

# Write with LLM
# https://g.co/gemini/share/35a049a6914b
def calculate_avalanche_effect(num_trials=100):
    flips_default = []
    flips_random = []
    
    generate_random_s_boxes = lambda: {i: [random.sample(range(16), 16) for _ in range(4)] for i in range(8)}

    print(f"Starting avalanche effect calculation for {num_trials} trials...")
    for i in tqdm(range(num_trials), desc="Processing..."):
        # 1. Create identical random key and plaintext for both methods
        key_bv = BitVector(intVal=random.getrandbits(56), size=56)
        plaintext_bv = BitVector(intVal=random.getrandbits(64), size=64)
        
        # Generate round keys
        round_keys = generate_round_keys(key_bv)
        
        # Generate s-box
        rand_s_boxes = generate_random_s_boxes()

        # 2. Encrypt using both methods
        illustrate_des_substitution.s_boxes = ORIGINAL_S_BOX
        cipher_default1 = DES(plaintext_bv, round_keys)
        illustrate_des_substitution.s_boxes = rand_s_boxes
        cipher_random1 = DES(plaintext_bv, round_keys)

        # 3. Flip one bit in the original plaintext
        flip_pos = random.randint(0, 63)
        plaintext_flipped = plaintext_bv.deep_copy()
        plaintext_flipped[flip_pos] = 1 - plaintext_flipped[flip_pos]

        # 4. Encrypt the flipped plaintext with both methods
        illustrate_des_substitution.s_boxes = ORIGINAL_S_BOX
        cipher_default2 = DES(plaintext_flipped, round_keys)
        illustrate_des_substitution.s_boxes = rand_s_boxes
        cipher_random2 = DES(plaintext_flipped, round_keys)

        # 5. Calculate the Hamming distance for both
        flips_default += [(cipher_default1 ^ cipher_default2).count_bits()]
        flips_random += [(cipher_random1 ^ cipher_random2).count_bits()]

    # Calculate the average
    avg_flips_default = mean(flips_default)
    avg_flips_random = mean(flips_random)

    print("\n--- Final Results ---")
    print(f"Default S-box: Average bits flipped = {avg_flips_default:.2f} / 64")
    print(f"Random S-box:  Average bits flipped = {avg_flips_random:.2f} / 64")
    
    # Using LLM https://g.co/gemini/share/3c4181eceaef
    t_statistic, p_value = ttest_ind(flips_default, flips_random)

    print(f"T-statistic: {t_statistic:.4f}")
    print(f"P-value: {p_value:.4f}")
    
    alpha = 0.05
    if p_value < alpha:
        print("✅ Result is different")
    else:
        print("❌ Result is not different")

if __name__ == "__main__":
    encrypt()
    decode()
    # calculate_avalanche_effect()