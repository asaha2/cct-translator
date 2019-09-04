import validateCct
import sys, csv, struct


def parse_sn_bin_file(cct_template_file, sn_bin_binary_file, output_file='RESULTS.csv'):
    """Opens the provided SN.BIN and iteratively parses based on passed CCT template rows data."""
    with open(cct_template_file, "r") as read_cct_file, \
        open(output_file, "w+") as write_cct_file, \
        open(sn_bin_binary_file, "rb") as binary_file:
        csv_reader = csv.reader(read_cct_file, delimiter=',')
        csv_writer = csv.writer(write_cct_file, delimiter=',')
        
        cct_size, proc_size = 0, 0
        line_count = 0        
        output_data = []        
        for row_data in csv_reader:
            line_count += 1
            
            if(line_count >=4):
                # capture cct size
                if(line_count == 5):
                    cct_size = int(row_data[8], 16)
                
                row_data[15:19] = ''
                byte_string = ''
                for index in range(int(row_data[0])):
                    byte_string += binary_file.read(1).hex()
                    
                # row_data.append(byte_string)
                row_data[15] = byte_string
                
                # # compare and update check value only for non-variable fields
                # if(row_data[13] == 'N'):
                    
                # incase of float, need to perform IEEE-754 conversion
                if row_data[12] == 'FLOAT':
                    float_value = struct.unpack('!f', bytes.fromhex(row_data[15]))[0]
                    row_data[15] = str(float_value).rstrip('.0')
                    bin_value = row_data[15]
                    cct_value = row_data[8].rstrip('.0')
                else:
                    cct_value = row_data[8].lower().lstrip('0x')
                    bin_value = row_data[15].lower().lstrip('0x')
                
                if(cct_value == bin_value):
                    row_data[16] = 'PASS'
                else:
                    row_data[16] = 'FAIL'
                # else:
                #     row_data[16] = 'IGNORED'
                
                output_data.append(row_data)
                
                # return if #size bytes processed
                proc_size += int(row_data[0])
                if(proc_size == cct_size):
                    break

        csv_writer.writerows(output_data)


if __name__ == "__main__":
    data = validateCct.parse_cct_file(sys.argv[1])
    if data:
        parse_sn_bin_file(sys.argv[1], sys.argv[2])
