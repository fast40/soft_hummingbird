import csv
import argparse


# initial_answer.csv, meta_abs_error_rank.csv, meta_meta_abs_error.csv

def join_csv_files(output_file, input_files):
    with open(output_file, 'w', newline='') as output_csvfile:
        writer = csv.writer(output_csvfile)

        input_files = [open(input_file, 'r', newline='') for input_file in input_files]
        input_readers = [csv.reader(input_file) for input_file in input_files]

        for rows in zip(*input_readers):
            writer.writerow(item for row in rows for item in row)
        
        for input_file in input_files:
            input_file.close()


def main():
    parser = argparse.ArgumentParser(description='Join CSV files into one big CSV file')

    parser.add_argument('output_file', help='Output CSV file')
    parser.add_argument('input_files', nargs='+', help='Input CSV files')

    args = parser.parse_args()

    join_csv_files(args.output_file, args.input_files)


if __name__ == '__main__':
    main()
