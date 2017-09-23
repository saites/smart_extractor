'''
A script to extract SMART data from GSF PDF files
'''
from tabula import convert_into
from tempfile import mkstemp
from pathlib import Path
import os
import sys


def read_data(filename):
    '''Attempts to strip out SMART recovery data from PDF, using tabula-py
    Returns a tuple of:
        - a list of entries, which should be "first,last,email,address,state,country"
        - a set of emails which were extracted from the PDF, but for which an entry
          was NOT extracted. The data for this entry must be manually extracted.
    '''
    # create a temporary file and use tabula to dump the content
    temp = mkstemp(text=True)
    convert_into(filename, temp[1],
                 output_format='csv', lattice=True, pages='all')
    os.close(temp[0])

    # clean it up by stripping out the data we don't care about, and reformatting weird text
    data = []
    emails = set()
    good_emails = set()
    with open(temp[1], 'rb') as F:
        for line in F:
            entry = [item.strip() for item in line.decode('UTF-8').split(',')]
            # collect emails so we can figure out which entries we couldn't process
            for email in [item for item in entry if '@' in item]:
                emails.add(email)
            # skip entries that don't look well-formatted
            if len(entry) < 5 or entry[0] == '""':
                continue

            joined = ','.join(entry[:6])
            good_emails.add(entry[2])
            data.append(','.join(entry[:6]))

    # clean up our temp file
    os.remove(temp[1])
    return data, emails.difference(good_emails)


def check_output_files(args):
    '''Make sure the output files don't exist, or that --force is used'''
    if not args.force and Path(args.output).exists():
        sys.stderr.write(
            '{} exists; use -f to force overwrite{}'.format(args.output, os.linesep))
        exit(1)

    if not args.force and Path(args.missed).exists():
        sys.stderr.write(
            '{} exists; use -f to force overwrite{}'.format(args.missed, os.linesep))
        exit(1)


def collect_filenames(args):
    '''Convert args to a list of input argument paths
    File paths are taken as-is. Directory paths are globbed for pdfs.
    Others are ignored.
    '''
    raw = [Path(p) for p in args.input]
    files = [p for p in raw if p.is_file()]
    for d in [p for p in raw if p.is_dir()]:
        files += d.glob('*.pdf')
    if len(files) == 0:
        sys.stderr.write(
            'No pdf files found in provided directories{}'.format(os.linesep))
        exit(1)
    return files


def process_from_cmd(args):
    '''Processes multiple files, using cmdline args'''
    check_output_files(args)
    files = collect_filenames(args)

    if not args.quiet and len(files) > 1:
        print('Processing {} files...{}'.format(len(files), os.linesep))

    entries = 0
    missed_count = 0
    with open(args.output, 'w') as output, open(args.missed, 'w') as missed:
        for pdf in files:
            if not args.quiet:
                print('Starting to process {}...'.format(pdf.name))

            try:
                results, emails = read_data(str(pdf.absolute()))
            except Exception as e:
                sys.stderr.write("Couldn't process {}: {}{}{}".format(
                    pdf.name, e, os.linesep, os.linesep))
                continue

            for line in results:
                output.write(line)
                output.write('\n')
            for e in emails:
                missed.write(e)
                missed.write('\n')

            entries += len(results)
            missed_count += len(emails)

            if not args.quiet:
                print('  ...grabbed {} entries; missed {} emails{}'.format(
                    len(results), len(emails), os.linesep))

    if not args.quiet and len(files) > 1:
        print('Finished processing: collected {} entries but missed {} emails'
              .format(entries, missed_count))


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(
        description='Extract SMART data from GSF PDF(s). ' +
        'Good entries are saved in output.csv; ' +
        "entries that couldn't be procssed are saved in output-missed.csv.")

    parser.add_argument('input', nargs='+',
                        help='a PDF file, or directory of PDF files, to process')
    parser.add_argument('-o', '--output', default='output.csv',
                        help='filename for extracted entries')
    parser.add_argument('-m', '--missed', default='missed.csv',
                        help='filename for emailed not found in extracted entries')
    parser.add_argument('-f', '--force', action='store_true',
                        help='force overwrite of existing output files')
    parser.add_argument('-q', '--quiet', action='store_true',
                        help="don't print processing info to the command line")

    process_from_cmd(parser.parse_args())
