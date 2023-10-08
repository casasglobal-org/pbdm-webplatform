#!/usr/bin/perl -w
# Script that writes color rules file to apply a unique color rule 
# to models raters based on overall range of data.

# Compared to rangeColorRule.pl, this version can use any
# combination of any number of colors.

# The central color will get a zero value.

# Author: Luigi Ponti
# Date: 24 April 2008

use strict;

# Set some variables.
my $HomeDir = $ARGV[0];
my $rule = $ARGV[1];
my $lowCut = $ARGV[2];
my $hiCut = $ARGV[3];
my $divergentRule = $ARGV[4];
my @table;
my @range;

# Read temporary files.
chdir ("$HomeDir/models_temp/");
opendir(DIR, "$HomeDir/models_temp/") || die "can't opendir $HomeDir/models_temp/: $!";

# Import model output files for reading
while (my $file = <*>)
{
    open (IN, "<$file") or die "Can't open $file for reading: $!";
	# Put rows as elements of the @table array.
	while (my $line = <IN>)
	{
		# Source: http://www.wellho.net/forum/Perl-Programming/New-line-characters-beware.html
		$line =~ s/\s+$//;                       
		push(@table, $line);
	}
	close IN;
	
	# Process input.            
	my $array_size = scalar @table;
	for (my $i = 0; $i < $array_size; $i++)
	{
		my @tempLine = split(/\t/, $table[$i]);
		# Removing leading white space: http://unix.org.ua/orelly/perl/cookbook/ch06_24.htm
		$tempLine[2] =~ s/^\s+//;
		# ...and also trailing white space -- just to be on the safe side.
		# Source: http://www.wellho.net/forum/Perl-Programming/New-line-characters-beware.html
		$tempLine[2] =~ s/\s+$//;    
		push(@range, $tempLine[2]);
	}
	@table = ();
}
closedir DIR;

# Sort and get maximum and minimun of overall range of data.
my @sortedRange = sort { $a <=> $b } @range;
my $min = $sortedRange[0];
my $max = $sortedRange[-1];

# Check if cutting points influence the range.
if ($hiCut ne "na")
{
	$max = $hiCut if $hiCut < $max;
}
$min = $lowCut if $lowCut > $min;

# Initialize color rule file.
chdir ("$HomeDir");
my $output = "customColorRule.txt";

# Put colors into an array.
my @colors = split(/-/, $rule);
# Compute number of colors and bands.
my $numOfColors = scalar @colors;
my $NumOfBands = $numOfColors - 1;
my $halfNumOfBands = ($numOfColors - 1) / 2;

if ($divergentRule eq "divNo")
{
	# Build array of coefficients.
	my $baseCoeff = 1 / $NumOfBands;
	my @coefficients;
	push(@coefficients, $min);
	for (my $i = 1; $i <= ($NumOfBands - 1); $i++)
	{
		push(@coefficients, ($min + ($i * $baseCoeff * ($max - $min))))
	}
	push(@coefficients, $max);
	
	# Print color rule file.
	open (OUTFILE, ">$output") or die "Can't open $output for writing: $!";
	for (my $i = 0; $i < $numOfColors; $i++)
	{
		print OUTFILE "$coefficients[$i] $colors[$i]\n"
	}
	print OUTFILE "end\n";
	close OUTFILE;
}
elsif ($divergentRule eq "divYes")
{
	# Build array of coefficients.
	my $baseCoeff = 1 / $halfNumOfBands;
	my @coefficients;
	push(@coefficients, $min);
	for (my $i = ($halfNumOfBands -1); $i >= 1; $i--)
	{
		push(@coefficients, ($i * $baseCoeff * $min))
	}	
	if (($numOfColors % 2) == 1)
	{
		push(@coefficients, 0)
	}
	else
	{
		push(@coefficients, (0, 0))
	}
	for (my $i = 1; $i <= ($halfNumOfBands - 1); $i++)
	{
		push(@coefficients, ($i * $baseCoeff * $max))
	}
	push(@coefficients, $max);

	# Print color rule file.
	open (OUTFILE, ">$output") or die "Can't open $output for writing: $!";
	for (my $i = 0; $i < $numOfColors; $i++)
	{
		print OUTFILE "$coefficients[$i] $colors[$i]\n"
	}
	print OUTFILE "end\n";
	close OUTFILE;
}

# Print file with the minimum value of data range.
my $minFile = "min.txt";
open (MIN, ">$minFile") or die "Can't open $minFile for writing: $!";
print MIN "$min";
close MIN;
# Print file with the maximum value of data range.
my $maxFile = "max.txt";
open (MAX, ">$maxFile") or die "Can't open $maxFile for writing: $!";
print MAX "$max";
close MAX;
