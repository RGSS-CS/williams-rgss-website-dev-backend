from better_profanity import profanity

if __name__ == "__main__":
    # Test the profanity filter
    test_text = "Shittestmanzs632"
    censored_text = profanity.contains_profanity(test_text)
    print(censored_text)  # Output: This is a **** test.