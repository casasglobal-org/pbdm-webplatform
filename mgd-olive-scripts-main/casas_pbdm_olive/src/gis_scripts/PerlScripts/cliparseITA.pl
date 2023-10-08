#!/usr/bin/perl -w
# Script that transform a string containing ET0 regions
# to a formula suitable for use in GRASS clipping
# Author: Luigi Ponti
# Date: 10 January 2006

use strict;
# Read string from GRASS parser.
my $HomeDir=$ARGV[0];
chdir ("$HomeDir"); 
my $file ="clipRegion.txt";
open (IN, "<$file") or die "Can't open $file for reading: $!";
# Put integers indicating regions into an array.
my @regions;
while (my $line = <IN>)
{
	@regions = split(/ /, $line);
}
close IN;

# Identify "zone" attribute for GRASS formula:
# "zone" is a column of the database connected
# to the evapotranspiration zones vector.
my $n =0;
my @formula;
foreach my $reg (@regions)
{
	chomp $reg;
	$formula[$n] = "(ISTAT=$reg)";
	$n++;
}
    
# Join features selected by attribute "zone" into
# a string to use in the clipping formula.
my $output = "formula.txt";
open (OUTFILE, ">$output") or die "Can't open $output for writing: $!";
print OUTFILE join(" or ", @formula);
close OUTFILE;