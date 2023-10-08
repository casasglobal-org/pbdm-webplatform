#!/usr/bin/perl -w
# Script that prints column and row names of model output files
# for proper input selection in the GRASS parser.
# The part that prints years for legend has been
# transferred to a printYear.pl script (NOTE).
# Author: Luigi Ponti
# Date: 2 March 2006

use strict;

# Import files in models directory for reading.
my $HomeDir=$ARGV[0];
my $models_dir = "$HomeDir/outfiles/";
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
		
		# Print column names just once.
		if ($fileNumber == 1)
		{
			my @columns = split(/\t/, $table[0]);
			my $n =1;
			print "\n";
			print "The following column names were found:\n";
			print "\n";
			foreach my $field (@columns)
				{
					$field =~ s/\s+$//;
					print "$n. $field\n";
					$n++;
				}
		}
		
		# Print row names just once.                
		if ($fileNumber == 1)
		{
			my $rowNum = scalar @table;
			print "\nNumber of rows is $rowNum.\n";
		}		 
	$fileNumber++;
	}
}
closedir DIR;

    
