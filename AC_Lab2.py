import pickle
from os.path import abspath 

CodingLength = 1
def count_file_symbols(filename):
    symbol_count = 0
    enters = {}
    input_file = open(filename,mode= "r",encoding = 'utf-8')
    input_text= input_file.read() 
    for char in input_text:  
        char_code=ord(char)
        if char_code in enters:
            enters[char_code]+=1
        else:
            enters[char_code]=1
        symbol_count = symbol_count + 1
    input_file.close()
    return symbol_count, enters 

def init_model(inputFilename): #функция прочтения данных из файла
    (symbol_count, ents) = count_file_symbols(inputFilename)
    
    low = 0.0
    freq = {}
    high = 0xFFFFFFFF #Предполагаем, что нужно работать с целочисленной арифметикой для больших алфавитов
    for ch_code in ents:
        ents[ch_code] = int(high * ents[ch_code] / symbol_count)
    
    for ch_code in ents:
            high = low + ents[ch_code]
            freq[ch_code] = (low, high)
            low = high
    #model_file = open(outputFilename, 'wb')
    #pickle.dump(freq, model_file) # Сохраняет его в файл (необходимый для декодирования)
                                  # в виде словаря. Файл двоичный, а для записи и чтения из него - модуль pickle   
    with open('codes.py', 'w+', encoding='UTF-8') as f:
        f.write('freq = '+str(freq))
    #model_file.close()
        

def read_model(): #функция прочтения данных из файла
    #input_file = open(modelFilename, 'rb')
    #freq = pickle.load(input_file)
    from codes import freq
    #input_file.close()
    return freq


def char_low_high(char, dictionary):
    char_code= ord(char)
    (low, high) = dictionary[char_code]
    return (low, high)


def add_symbol_to_coding_sentence(sent_low, sent_high, freq, symbol):
    (symbol_low, symbol_high) = char_low_high(symbol, freq)
    return (sent_low + (sent_high - sent_low) * symbol_low, sent_low + (sent_high - sent_low) * symbol_high)



def encoding(input_filename, freq, outputfilename):
    input_file = open(input_filename, 'r', encoding = 'utf-8')
    output_file = open(outputfilename, 'wb')
    input_text=input_file.read()
    
    coding_result = []
    count = CodingLength 
    for char in input_text:
        if count >= CodingLength:
            (low, high) = char_low_high(char, freq)
            count = 1
        else:
            (low, high) = add_symbol_to_coding_sentence(low, high, freq, char)
            count += 1
            
        if count >= CodingLength:
            coding_result.append((count, low+(high-low)/2))
    if count != 0:
        coding_result.append((count, low + (high - low) / 2))
    pickle.dump(coding_result, output_file, protocol=1)
    input_file.close()
    output_file.close()



def reverse_map(char_to_range):
    range_to_char = {}
    for key in char_to_range:
        range_interv = char_to_range[key]
        range_to_char[range_interv] = key
    return range_to_char


def get_first_char_range(value, range_to_char):
    for key in range_to_char:
        (low, high) = key
        if ((low <= value) and (value <= high)):
            return (low, high)
    return [-1,-1]



def decoding(input_filename, range_to_char, outputfilename):
    input_file = open(input_filename, 'rb')
    codes = pickle.load(input_file)
    input_file.close()
    output_file = open(outputfilename, 'w+')
    for (length, code) in codes:
        for number in range(length):
            char_range = get_first_char_range(code, range_to_char)
            char = chr(range_to_char[char_range])
            output_file.write(char)
            (low, high) = char_range
            code = (code-low)/(high-low)
    output_file.close()



mode = int(input("В каком режиме запустить программу? 1- кодирование, 2 - декодирование"))
if(mode==1):
    txt = input("Введите полный путь к файлу, который хотите закодировать: ")
    init_model(txt)
    char_to_range = read_model()
    #range_to_char = reverse_map(char_to_range)
    print(char_to_range)
    encoding('input.txt', char_to_range, 'encode_AC.txt')
    print("Закодированный текст находится в файле: ", abspath('encode_AC.txt')) 
if(mode==2):
    char_to_range = read_model()
    range_to_char = reverse_map(char_to_range)
    decoding('encode_AC.txt', range_to_char, 'decode_AC.txt')
    print("Декодированный текст находится в файле: ", abspath('decode_AC.txt'))