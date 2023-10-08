#!/usr/bin/perl -w
# Script that writes a HTML visual summary for CASAS models
# Author: Luigi Ponti
# Date: 16 April 2006

use strict;

# Read Directory where maps are saved and 
# other parameters from script arguments.
my $SaveDir=$ARGV[0];
my $LegendString=$ARGV[1];
my $MapPar=$ARGV[2];
my $LowerCut=$ARGV[3];
my $UpperCut=$ARGV[4];
my $AltClip=$ARGV[5];
my $SurfCut=$ARGV[6];
my $EtoClip=$ARGV[7];
my $Plots=$ARGV[8];

# Read string from GRASS parser.
chdir ($SaveDir);
my $file ="$LegendString.html";
open (OUT, ">$LegendString.html") or die "Can't open $LegendString.html for writing: $!";

print OUT '<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN" "http://www.w3.org/TR/html4/strict.dtd">';
print OUT "\n";
print OUT "<html>";
print OUT "\n";
print OUT "<head>";
print OUT "\n";
print OUT "<title>$LegendString - Visual Summary</title>";
print OUT "\n";
print OUT '<meta http-equiv="content-type" content="text/html; charset=iso-8859-1" >';
print OUT "\n";
print OUT '</head>';
print OUT "\n";
print OUT '<body>';

# Import files in models directory for reading.
opendir(DIR, $SaveDir) || die "can't opendir $SaveDir: $!";

# Read map names, write them to html file,
# and create links to stat reports.
print OUT "\n<h1>Report for \"$LegendString\"</h1>";
print OUT "\n<h2>Output maps</h2>";
while (my $file = readdir(DIR))
{
	if ($file =~ /.\.png/ && $file !~ /PLOT/)
	{
		if ($file !~ /HIST/)			
		{
			$file =~ s/\.png//;
			print OUT "\n<a href=\"$file.txt\"><img src=\"$file.png\" width=\"32%\"></a>";
		}
	}
}
print OUT "\n<p><i>Please, click on images to see stat report.</i></p>";

# Print a link to page with barchart plots.
if ($Plots)
{
	print OUT "\n<p><i>You may also see raster statistics as barcharts";
	print OUT " (<a href=\"$LegendString-PLOTa.html\" target=\"_blank\">zoned</a>";
	print OUT " and <a href=\"$LegendString-PLOTb.html\" target=\"_blank\">overall</a>)";
	print OUT " and as cell frequency <a href=\"$LegendString-PLOTc.html\" target=\"_blank\">histogram</a>.</i></p>";
}

# Print some other useful stuff.
print OUT "\n<h2>Mapping parameters</h2>";
print OUT "\n<ul>";
print OUT "\n<li>Parameter mapped: $MapPar";
print OUT "\n<li>Lower cutting point: $LowerCut";
print OUT "\n<li>Upper cutting point: $UpperCut";
print OUT "\n<li>Region clip: $EtoClip";
print OUT "\n<li>Altitude clip: $AltClip m";
print OUT "\n<li>Stations above altitude clip were used to interpolate: $SurfCut";
print OUT "\n</ul>";

# Append log with input files.
print OUT "\n<h2>Input file log</h2>";
		open (IN, "<$LegendString.log") or die "Can't open $LegendString.log for reading: $!";
		while (my $line = <IN>)
		{
			if ($line =~ / /)
			{
				print OUT "\n$line<br>";
			}
			else
			{
				print OUT "\n<ul>";
				print OUT "\n<li>$line</li>";
				print OUT "\n</ul>";
			}
		}
		close IN;

print OUT '</body>';
print OUT '</html>';
close OUT;
closedir DIR;