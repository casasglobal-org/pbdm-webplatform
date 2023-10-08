#!/usr/bin/perl -w
# Script that takes the output of r.stats and
# puts it in a form suitable to produce a plot.

# Author: Luigi Ponti
# Date: 15 September 2006

use strict;

# Read directory where maps are saved and 
# other parameters from script arguments.
my $SaveDir=$ARGV[0]; 

# Read string from GRASS parser. 
chdir ("$SaveDir");
opendir(DIR, $SaveDir) || die "Can't opendir $SaveDir: $!";

# Read *.rep files produced by r.stats
while (my $file = readdir(DIR))
{
	if ($file =~ /.\.rep/)
	{
		open (IN, "<$file") or die "Can't open $file for reading: $!";
		# Put rows as elements of the @table array.
		my @table;
		my @newTable;
		while (my $line = <IN>)
		{
			chomp $line;
			push(@table, $line);
		}
		close IN;
		
	# Split rows in cells and rearrange them        
	my $array_size = scalar @table;
	my @firstLine = split(/\t/, $table[0]);
	my @lastLine = split(/\t/, $table[$array_size-1]);
	# Get the lowest and higest zone index in table
	my $firstZone = $firstLine[0];	 
	my $currZone = $firstZone;
	my $prevZone = $currZone;
	my @newLine = (0,0,0,0,0);
	foreach my $row (@table)
	{
		my @tempLine = split(/\t/, $row);
		$currZone = $tempLine[0];
		if ($currZone == $prevZone)
		{
			if ($tempLine[1] == 1)
			{
				$newLine[1] = $tempLine[2];
			} 
			elsif ($tempLine[1] == 2)
			{
				$newLine[2] = $tempLine[2];
			} 
			elsif ($tempLine[1] == 3) 
			{
				$newLine[3] = $tempLine[2];
			}
			elsif ($tempLine[1] == 4)
			{
				$newLine[4] = $tempLine[2];
			}
			$newLine[0] = $currZone;
		}
		elsif ($currZone != $prevZone)
		{
		my $tablePush = join ("\t", @newLine);
		push(@newTable, "$tablePush\n");
		@newLine = (0,0,0,0,0);
		if ($tempLine[1] == 1)
			{
				$newLine[1] = $tempLine[2];
			} 
			elsif ($tempLine[1] == 2)
			{
				$newLine[2] = $tempLine[2];
			} 
			elsif ($tempLine[1] == 3) 
			{
				$newLine[3] = $tempLine[2];
			}
			elsif ($tempLine[1] == 4)
			{
				$newLine[4] = $tempLine[2];
			}
			$newLine[0] = $currZone;
		}
		$prevZone = $currZone
	}
	# Oherwise the last line does not get printed
	my $tablePush = join ("\t", @newLine);
	push(@newTable, "$tablePush\n");
	$file =~ s/\.rep/.tab/;
	my $output = "$file";
	open (OUTFILE, ">$output") or die "Can't open $output for writing: $!";
	print OUTFILE join ("", @newTable);                    
	close OUTFILE;
	}
	elsif ($file =~ /.\.tot/)
	{
		open (IN, "<$file") or die "Can't open $file for reading: $!";
		# Put rows as elements of the @table array.
		my @table;
		while (my $line = <IN>)
		{
			chomp $line;
			push(@table, $line);
		}
		close IN;		
		my @newLine = (0,0,0,0,0);
		foreach my $row (@table)
		{
			my @tempLine = split(/\t/, $row);
			if ($tempLine[0] == 1)
			{
				$newLine[1] = $tempLine[1];
			} 
			elsif ($tempLine[0] == 2)
			{
				$newLine[2] = $tempLine[1];
			} 
			elsif ($tempLine[0] == 3) 
			{
				$newLine[3] = $tempLine[1];
			}
			elsif ($tempLine[0] == 4)
			{
				$newLine[4] = $tempLine[1];
			}
		}
		$newLine[0] = 1;
		$file =~ s/\.tot/.tabTot/;
		my $output = "$file";
		open (OUTFILE, ">$output") or die "Can't open $output for writing: $!";
		print OUTFILE join ("\t", @newLine);                    
		close OUTFILE;		
	}
}
closedir DIR;