from analyzer import analyze_string


if __name__ == '__main__':

    input_str = '(1 <> 3) < (2 + 3) / 4'

    ans = analyze_string(input_str=input_str)
    print(ans)
