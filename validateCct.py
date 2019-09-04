import sys
import csv
from enum import Enum


class ReturnCode(Enum):
    TEST_CASE_0 = 0
    TEST_CASE_1 = 1
    TEST_CASE_2 = 2
    TEST_CASE_3 = 3


class ValidationException(Exception):
    pass


def validate_fields(field_list):
    """Performs validation tests on provided row fields."""
    # update row count at beginning of every iteration
    validate_fields.row_count += 1

    # dictionary definition of data type-byte size and other field value requirements
    data_type_size = {'UINT8': 1, 'UINT16': 2, 'UINT32': 4, 'INT32': 4, 'FLOAT': 4, 'CHAR': 1}

    # compare columns A and M
    try:
        check_status = (int(field_list[0]) != int(data_type_size[field_list[12]]))
        if check_status:
            raise ValidationException()
    except(ValidationException, ValueError):
        return (ReturnCode.TEST_CASE_1, validate_fields.row_count, 
                validate_fields.size_byte, validate_fields.offset)

    # update byte count once field byte size has been verified
    validate_fields.size_byte += int(field_list[0])

    # compare columns F, P and R
    try:
        check_status = (int(field_list[5], 16) != validate_fields.offset or 
                        int(field_list[15]) != validate_fields.offset or 
                        int(field_list[17], 16) != validate_fields.offset)
        if check_status:
            raise ValidationException()
    except(ValidationException, ValueError):
        return (ReturnCode.TEST_CASE_2, validate_fields.row_count, 
                validate_fields.size_byte, validate_fields.offset)

    # compare columns Q and S
    try:
        check_status = (int(field_list[16]) != validate_fields.size_byte or 
                        int(field_list[18], 16) != validate_fields.size_byte)
        if check_status:
            raise ValidationException()
    except(ValidationException, ValueError):
        return (ReturnCode.TEST_CASE_3, validate_fields.row_count, 
                validate_fields.size_byte, validate_fields.offset)

    # update offset once all other verifications have passed
    validate_fields.offset += int(
        field_list[0])

    return None


def parse_cct_file(template_file):
    """Opens the provided csv file and iteratively parses and processes the rows."""
    with open(template_file) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')

        # dictionary definition of specific line no.-field values
        row_field_value = {7: '0xA0', 8: '0x194'}

        # init static variable
        validate_fields.row_count = 0
        validate_fields.size_byte = 0
        validate_fields.offset = 0

        # keep track and ignore first 3 lines
        line_count = 0
        offset_data = []
        size_value = 0

        # iterate through all row fields and run validation checks
        for row_data in csv_reader:
            line_count += 1
            if(line_count >= 4):
                # size needs to be divisible by 4
                if(line_count == 5):
                    if(int(row_data[8], 16) % 4):
                        print("Error: Size not divisible by 4")
                        return None
                    else:
                        size_value = int(row_data[8], 16)

                # check General and ID section size
                if(line_count == 7 or line_count == 8):
                    if(hex(int(row_data[8], 16))) != hex(int(row_field_value[line_count], 16)):
                        print("CCT Validation Test FAILED: %s = %x" %
                              (row_data[6], hex(int(row_data[8]))))
                        return None

                test_status = validate_fields(row_data)
                if test_status != None:
                    print("CCT Validation Test FAILED: %s %d %d %d" % 
                          (test_status[0].name, test_status[1], test_status[2], test_status[3]))
                    return None
                else:
                    offset_data.append(int(row_data[0]))

                    # there can be additional rows in the spreadsheet, but we're
                    # only interested in CCT_SIZE bytes equivalent
                    if(sum(offset_data) == size_value):
                        return offset_data

        return offset_data


if __name__ == "__main__":
    data = parse_cct_file(sys.argv[1])
    if data:
        # print(data)
        print("CCT Validation test PASSED")
    else:
        # print(data)
        print("CCT Validation test FAILED")
