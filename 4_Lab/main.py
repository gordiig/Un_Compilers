from analyzer import analyze_string


if __name__ == '__main__':
    input_str = '(2 - 9) <> 3 + ((4 * 1) == 6)'

    ans = analyze_string(input_str=input_str)
    print(ans)
