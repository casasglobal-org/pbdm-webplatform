#!/usr/bin/perl -w
# Script that transform a string containing attribute DBF
# values to a formula suitable for use in GRASS clipping.
# This version takes more arguments so that also attribute
# column name, and input and output files can be specified.
# _TC means type check--it checks type of column to know
# if quoting is necessary. Number or string.

# Author: Luigi Ponti
# Date: 26 January 2010

use strict;
# Read string from GRASS parser.
my $HomeDir = $ARGV[0];
my $fieldName = $ARGV[1];
my $fieldType = $ARGV[2];
my $input = $ARGV[3];
my $output = $ARGV[4];

chdir ("$HomeDir"); 
open (IN, "<$input") or die "Can't open $input for reading: $!";
# Put integers indicating regions into an array.
my @regions;
while (my $line = <IN>)
{
	# This is for compatibility with scripts that take space-separted lists
	# as input. The EurMedGrape script uses a list of country names that
	# is comma separated because some country names include spaces, and hence
	# the script would not know where to split based on spaces.
	if ($line =~ /,/)
	{
		@regions = split(/,/, $line);
	}
	else
	{
		@regions = split(/ /, $line);
	}
}

close IN;

# Formulate database query
my $n =0;
my @formula;
if ("$fieldType" eq 'number')
{ # It is a number
    foreach my $reg (@regions)
    {
        chomp $reg;
        $formula[$n] = "($fieldName=$reg)";
        $n++;
    }
}
else
{ # It is a string, you need to quote it
    foreach my $reg (@regions)
    {
        chomp $reg;
        $formula[$n] = "($fieldName=\'$reg\')";
        $n++;
    }
}
# Write the query
open (OUTFILE, ">$output") or die "Can't open $output for writing: $!";
print OUTFILE join("or", @formula);
close OUTFILE;
