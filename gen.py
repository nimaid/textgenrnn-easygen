#! /usr/bin/python3
import argparse, os, time, datetime, zipfile, tempfile, shutil

tick_skip = 1

parser = argparse.ArgumentParser(description=
    'Use a brain to generate text.\nUsage: python3 gen.py -b brain_path -l length')
parser.add_argument('-b', '--brain', help =
    'Path to brain zip archive.',
    required = True, nargs = 1, type = str)
parser.add_argument('-l', '--length', help =
    'Length of text to generate.',
    required = True, nargs = 1, type = int)
parser.add_argument('-f', '--file', help =
    'File to save to.',
    required = False, default = '', nargs = 1, type = str)
parser.add_argument('-t', '--temp', help =
    'Temperature of output. (Default = 1.0)',
    required = False, default = 1.0, nargs = 1, type = float)
parser.add_argument('-n', '--number', help =
    'Number of samples to generate. (Default = 1)',
    required = False, default = 1, nargs = 1, type = int)
args = vars(parser.parse_args())

base_filename = None
try:
    base_filename = args['file'][0]
    if base_filename[-4:].lower() == '.txt':
        base_filename = base_filename[:-4]
except:
    base_filename = args['file']

#extract brain
tempdir = tempfile.gettempdir()
tempdir = os.path.join(tempdir, 'textgenrnn-easygen')
if not os.path.exists(tempdir):
    os.mkdir(tempdir)
with zipfile.ZipFile(args['brain'][0], 'r') as zf:
    zf.extractall(tempdir)

#generate samples
samples = None
try:
    samples = args['number'][0]
except:
    samples = args['number']

for sample in range(samples):
    #generate text
    start_time = time.time()
    from textgenrnn import textgenrnn

    textgen = textgenrnn(weights_path = os.path.join(tempdir, 'weights.hdf5'),
                         vocab_path = os.path.join(tempdir, 'vocab.json'),
                         config_path = os.path.join(tempdir, 'config.json'))

    print('\nCreating sample {}/{}...'.format(sample + 1, samples))
    print('Creating {} characters...'.format(args['length'][0]))
    text = textgen.generate(max_gen_length = args['length'][0],
                            return_as_list = True,
                            temperature = args['temp'])[0]

    gen_secs = time.time() - start_time
    gen_time =  str(datetime.timedelta(seconds=gen_secs)).split(':')
    time_text = str(round(float(gen_time[-1]))) + " seconds"
    if len(time_text) >= 2:
        mins = gen_time[-2]
        if mins[0] == '0':
            mins = mins[1:]
        if mins not in ('', '0'):
            time_text = mins + " minutes, " + time_text
    if len(time_text) >= 3:
        hours = gen_time[-3]
        if hours[0] == '0':
            hours = hours[1:]
        if hours not in ('', '0'):
            time_text = hours + " hours, " + time_text
    print('Done making text! It took {}.'.format(time_text))
    print('\nText sample {}:\n'.format(str(sample+1)))
    print(text)
    if base_filename != '':
        filename = base_filename + '_' + str(sample + 1) + '.txt'
        print('\nSaving to "{}"'.format(filename))
        with open(filename, 'w+') as f:
            f.write(text)
        print('Saved to "{}"!'.format(filename))
print('\nDone generating {} samples! Cleaning up...'.format(samples))
shutil.rmtree(tempdir)
print('All done! Enjoy your novel... or whatever this program made.')
