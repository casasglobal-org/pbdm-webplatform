#!/usr/bin/perl -w
# Script that prints analysis years to a file according to
# GRASS parser input for use in legend.
# Author: Luigi Ponti
# Date: 2 March 2006

use strict;

# Import files in models directory for reading.
my $HomeDir=$ARGV[0];
my $models_dir="$HomeDir/outfiles/";
opendir(DIR, $models_dir) || die "can't opendir $models_dir: $!";
my $fileNumber = 1;
my @years;
while (my $file = readdir(DIR))
    {
        if ($file =~ /.\.txt/)
            {
                chdir ("$HomeDir/outfiles/");
                open (IN, "<$file") or die "Can't open $file for reading: $!";
                
                 # Put rows as elements of the @table array.
                my @table;
                while (my $line = <IN>)
                    {
                        push(@table, $line);
                    }
                close IN;
                
                # Print years to a text file.                
                chdir ("$HomeDir"); 
                my $file ="inputPar.txt";
                open (IN, "<$file") or die "Can't open $file for reading: $!";

                # Put integers indicating columns into an array.
                my @inputs;
                my $inputs;
                while (my $line = <IN>)
                    {
                        @inputs = split(/\s/, $line);
                    }
                close IN;
                my $yearColumn = $inputs[3] - 1;
                
                chdir ("$HomeDir");                
                my @columns = split(/\t/, $table[1]);
                $years[$fileNumber-1] = $columns[$yearColumn];
                my $output = "year$fileNumber.txt";
                open (OUTFILE, ">$output") or die "Can't open $output for writing: $!";
                print OUTFILE " $columns[$yearColumn]\n";
                close OUTFILE;
                
            $fileNumber++;
            }
    }
closedir DIR;

# Join years of interest to the analysis
# and print them to a text file.
#~ chdir ("/home/andy/");
#~ my $output = "years$fileNumber.txt";
#~ open (OUTFILE, ">$output") or die "Can't open $output for writing: $!";
#~ print OUTFILE join(" ", @years);
#~ close OUTFILE;

    
