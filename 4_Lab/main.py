from analyzer import analyze_string


if __name__ == '__main__':

    input_str = '1 < 2'
    ans = analyze_string(input_str)
    print(f'Ans is {ans}, should be: 12<')

    input_str = '3 <> 4'
    ans = analyze_string(input_str)
    print(f'Ans is {ans}, should be: 34<>')

    input_str = '1 + 2 < 3 - 4'
    ans = analyze_string(input_str)
    print(f'Ans is {ans}, should be: 12+34-<')

    input_str = '1 + 2 < 3 + 4 / 5'
    ans = analyze_string(input_str)
    print(f'Ans is {ans}, should be: 12+345/+<')

    input_str = '1 + 2 < (3 + 4) / 5'
    ans = analyze_string(input_str)
    print(f'Ans is {ans}, should be: 12+34+5/<')

    input_str = '(1 <> 3) < (2 + 3) / 4'
    ans = analyze_string(input_str)
    print(f'Ans is {ans}, should be: 13<>23+4/<')
