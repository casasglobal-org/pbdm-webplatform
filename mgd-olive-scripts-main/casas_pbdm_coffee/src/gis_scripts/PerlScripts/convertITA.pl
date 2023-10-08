#!/usr/bin/perl -w
# Script that tweaks output tables form CASAS systems models
# for import to GRASS-GIS, interpolation & visualization.

# This version accept outfiles names such as as "Olive-02Mar06-00003.txt".

# Author: Luigi Ponti
# Date: 13 April 2006

use strict;

# Create a temporary folder for tweaked files.
my $HomeDir=$ARGV[0];
mkdir ("$HomeDir/models_temp/", 0777);

# Read string from GRASS parser.
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

# Import files in models directory for reading.
my $models_dir = './outfiles/';
opendir(DIR, $models_dir) || die "can't opendir $models_dir: $!";

# Set column numbers imported from GRASS parser as array indices
# and make the scope of correspondent variable wide enough by keeping
# them out of the loop.
my $lon = $inputs[0] - 1;
my $lat = $inputs[1] - 1;
my $par = $inputs[2] - 1;
my $parName;
# Import model output files for reading
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
			# Strip off all trailing white spaces - tabs, spaces, new lines and returns as well. 
			# This makes your code work on Unix and Linux whether the input file is from Windows or from Unix.  
			# As a side effect, it also removes any trailing whitespace on each line which is usually but not always an advantage.
			# Source: http://www.wellho.net/forum/Perl-Programming/New-line-characters-beware.html
			$line =~ s/\s+$//;                       
			# chomp $line;
			push(@table, $line) if $line =~ /\S/;
		}
		close IN;
		
		# Make longitude negative (necessary for import to LatLong location).            
		my $array_size = scalar @table; 
		for (my $i = 1; $i < $array_size; $i++)
		{
			my @tempLine = split(/\t/, $table[$i]);                                              
			$tempLine[$lon] = $tempLine[$lon];
			
			# Get name of the parameter being mapped.
			if ($i == 1)
			{
				my @tempLine = split(/\t/, $table[0]);
				$parName = "$tempLine[$par]";
				chomp $parName;
			}                        
			$table[$i] = join("\t", $tempLine[$lon], $tempLine[$lat], "$tempLine[$par]\n");
		}				   
			
		# Get rid of column names (as to GRASS 6.0.0, there is no way ot skip header line).
		shift(@table); 
		
		# Write tweaked files to the temporary directory from where they
		# should be imported by the main shell script.
		my $file2;
		chdir ("../models_temp/");
		# $file =~ tr/OUT.*\.txt/\n/;
		$file =~ s/\.txt//;
		$file2 = join("",$parName,"_", $file);
		my $output = "$file2";
		open (OUTFILE, ">$output") or die "Can't open $output for writing: $!";
		print OUTFILE join ("", @table);                    
		close OUTFILE;                
	}
}
closedir DIR;