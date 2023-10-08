#!/usr/bin/perl -w
# Script that transform a string containing attribute DBF
# values to a formula suitable for use in GRASS clipping.
# This version takes more arguments so that also attribute
# column name, and input and output files can be specified.

# Author: Luigi Ponti
# Date: 26 January 2010

use strict;
# Read string from GRASS parser.
my $HomeDir=$ARGV[0];
my $fieldName=$ARGV[1];
my $input=$ARGV[2];
my $output=$ARGV[3];

chdir ("$HomeDir"); 
open (IN, "<$input") or die "Can't open $input for reading: $!";
# Put integers indicating regions into an array.
my @regions;
while (my $line = <IN>)
{
	@regions = split(/ /, $line);
}
close IN;

# Formulate database query
my $n =0;
my @formula;
foreach my $reg (@regions)
{
	chomp $reg;
	$formula[$n] = "($fieldName=\'$reg\')";
	$n++;
}
    
# Write the query
open (OUTFILE, ">$output") or die "Can't open $output for writing: $!";
print OUTFILE join("or", @formula);
close OUTFILE;
