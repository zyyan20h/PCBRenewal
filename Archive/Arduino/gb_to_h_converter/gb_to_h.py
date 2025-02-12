def gb_to_header(input_file, output_file, array_name):
    with open(input_file, "rb") as gb_file:
        rom_data = gb_file.read()

    with open(output_file, "w") as header_file:
        header_file.write(f"unsigned char {array_name}[] = {{\n")

        # Write the data as comma-separated hex values
        for i, byte in enumerate(rom_data):
            if i % 12 == 0:  # Format to have 12 bytes per line
                header_file.write("\n    ")
            header_file.write(f"0x{byte:02X}, ")

        # Remove last comma and close the array
        header_file.write("\n};\n")

    print(f"{input_file} converted to {output_file} as array {array_name}.")

gb_to_header("breakout.gb", "rom.h", "game_rom")