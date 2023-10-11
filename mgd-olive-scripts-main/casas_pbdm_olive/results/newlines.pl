#!/usr/bin/perl -w
# for %v in (*.txt) do perl newlines.pl -n "CRLF" "%v"
# unix version:
# for filename in *.txt; do perl "/PathTo/newlines.pl" -n "CRLF" $filename; done
use strict;
use Getopt::Std;
use File::Find;



# get the options:
my %opts;
getopts('f:n:h', \%opts) || usage();
usage() if (!$opts{'n'} || $opts{'h'});

# if no files were specified, we'll convert everything in the current directory:
push(@ARGV, '.') unless @ARGV;

my $newline = $opts{'n'};
usage() if ($newline =~ /[^CRLF]/i);

$newline =~ s/CR/\015/i;
$newline =~ s/C/\015/i;
$newline =~ s/R/\015/i;
$newline =~ s/LF/\012/i;
$newline =~ s/L/\012/i;
$newline =~ s/F/\012/i;

foreach my $filename (@ARGV)
{
	# traverse the directory tree and look at each file:
	find(sub { convertNewlines() }, $filename);
}





sub convertNewlines
{
	my $filename = $_;
	
	# don't mess with it unless it's a text file:
	return unless (-T $filename);

	open(FILE, "< $filename")
		or die "Couldn't open file ($filename) for reading: $!";

	my $converted_text;
	my $line_endings_converted = 0;
	while (my $line = <FILE>)
	{
		$line_endings_converted +=
			($line =~ s/(?:\015\012|\015|\012)/$newline/g);
		$converted_text .= $line;
	}

	# now save it, and binmode it so no additional conversion is done to
	# the line endings:
	open(FILE, "> $filename")
		or die "Couldn't open file ($filename) for writing: $!";
	binmode FILE;
	print FILE $converted_text;
	close FILE;

	print "Converted $line_endings_converted newlines in \"$filename\" " .
	      "to $opts{'n'}.\n";
}





sub usage
{
	print <<'END_OF_USAGE';
This script can be used to convert the line endings in files to Unix, Windows,
or MacOS line endings.

Usage:
 $ newlines -n NEWLINE [FILENAMES...]

Arguments:
	-n   The newline sequence that the line endings in the files you
	     specified should be converted to. Either "CR" or "R" for carriage
	     return, "LF" or "L" for linefeed, or "CRLF" for carriage
	     return/linefeed.
Flags:
	-h   Displays this message.
END_OF_USAGE

	exit;
}
