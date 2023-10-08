#!/usr/bin/perl -w
# Script that transforms a string with categories
# of Voronoi polygons containing zero value points
# to a formula suitable for use in GRASS v.extract
# Author: Luigi Ponti
# Date: 4 Aprile 2006

use strict;
# Read string from GRASS parser.
my $HomeDir=$ARGV[0];
chdir ("$HomeDir"); 
my $file ="voronoi.txt";
open (IN, "<$file") or die "Can't open $file for reading: $!";
# Put categories of voronoi polygons into an array.
my @regions;
while (my $line = <IN>)
    {
        push(@regions, $line);
    }
close IN;

# Identify categories for GRASS formula to
# select from vector of Voronoi polygons.
my $n =0;
my @formula;
foreach my $reg (@regions)
    {
        chomp $reg;
        $formula[$n] = "(cat=$reg)";
        $n++;
    }
    
# Join features selected by category into
# a string to use in the clipping formula.
my $output = "voronoiFormula.txt";
open (OUTFILE, ">$output") or die "Can't open $output for writing: $!";
print OUTFILE join(" or ", @formula);
close OUTFILE;