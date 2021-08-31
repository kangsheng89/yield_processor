import csv
import sys

# list to store processing data
output = []


# avoid loading large csv into memory
def rows_from_a_csv_file(filename, dialect='excel'):
    with open(filename, 'r') as csv_file:
        reader = csv.reader(csv_file, dialect)
        for row in reader:
            # using yield as generator
            yield row


def calculation(ori_price, ori_volumn, quantity, price):
    ori_value = ori_price * ori_volumn
    current_value = quantity * price
    new_volumn = ori_volumn + quantity
    # no truncation to make sure the calculation correctness
    weighted_avg_price = (ori_value + current_value) / (ori_volumn + quantity)

    return weighted_avg_price, new_volumn


def update_max(max, curr):
    if max < curr:
        max = curr

    return max


def process(row):
    global output
    time = int(row[0])
    symbol = row[1]
    quantity = int(row[2])
    price = int(row[3])

    res = list(filter(lambda stock: stock['symbol'] == symbol, output))
    # initial case, no symbol found in list, insert the symbol and initialize some values
    if not res:
        stock = {'symbol': symbol,
                 'MaxTimeGap': 0,
                 'Volume': quantity,
                 'WeightedAvgPrice': price,
                 'MaxPrice': price,
                 'LastTimestamp': time,  # placeholder for last known time
                 }
        output.append(stock)

    else:
        stock = res[0]

        curr_time_gap = time - stock['LastTimestamp']
        stock['LastTimestamp'] = time

        stock['WeightedAvgPrice'], stock['Volume'] = calculation(stock['WeightedAvgPrice'], stock['Volume'], quantity,
                                                                 price)

        stock['MaxPrice'] = update_max(stock['MaxPrice'], price)
        stock['MaxTimeGap'] = update_max(stock['MaxTimeGap'], curr_time_gap)


def csv_writer(file, to_output):
    # sort the symbol before write into csv
    to_output.sort(key=lambda k: k['symbol'])

    try:
        with open(file, 'w', newline="") as csvfile:
            csv_columns = ['symbol', 'MaxTimeGap', 'Volume', 'WeightedAvgPrice', 'MaxPrice']
            writer = csv.DictWriter(csvfile, fieldnames=csv_columns, dialect='excel')
            for data in to_output:
                # remove last time stamp as it is not required
                data.pop('LastTimestamp')

                # truncation of the Weighted Average price when writing into csv
                data['WeightedAvgPrice'] = data['WeightedAvgPrice'].__trunc__()
                writer.writerow(data)

    except IOError:
        print("I/O error")


if __name__ == '__main__':
    # take in input and output from the argument
    csv_file_path = sys.argv[1]
    csv_output_path = sys.argv[2]

    for row in rows_from_a_csv_file(csv_file_path):
        process(row)

    csv_writer(csv_output_path, output)
