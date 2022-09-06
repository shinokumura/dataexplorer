#!/usr/bin/perl
###########################################################################
#
#  Create list file for fpy experimental data.
#  To run the FY data for libraries, refer https://github.com/shinokumura/tabfylibs
#                                                       2021 May by SO
#
###########################################################################


use strict;
use warnings;
use File::Basename;

my $topdir  = "/Users/okumuras/Documents/nucleardata/libraries/libraries/FY/";

my $cmd = "rm -rf " . $topdir . "*/*/exfor/*/*.list";
system($cmd);

&make_yalist();

sub make_yalist{
    my @files = glob($topdir . '*/*/exfor/*/*');

    foreach my $f (@files){
	my $basename = basename($f);
	my $dirname  = dirname($f);
	my @en = ();
	my @pt = ();
	my ($zz,$aa, $z, $a, $iso, $y, $dy) = (0,0,0,0,0,0,0);
	my @dataset = split(/-/, $basename);
	$basename =~ /(\S+-MT4[56][490])(?)/;
	print "$dirname, $1, list\n";
	my $outfile_a =  $dirname . "/" . $1 . "-YA.list";
	my $outfile_za =  $dirname . "/" . $1 . ".list";

	open(EN, "$f") or die "No file";
	while(<EN>){
	    my $line  =  $_;
	    chomp $line;
	    if ($line =~ /E-inc/){
		@en = split(/\s+/, $line);
	    }
	    if ($line =~ /Data points/){
		@pt = split(/\s+/, $line);
	    }
	    if ($line =~ /^\s/){
		$line =~ s/^\s+//;
		($z, $a, $iso, $y, $dy) = split(/\s+/, $line);

		if ($z eq "0****"){print "ERROR FILE\n";  $zz = -1; next;}
		else {$zz += $z; $aa +=$a};

		print "$z, $a, $iso, $y, $dy\n";
	    }
	}
	
	if ($zz == 0 && $aa !=0){
	    open(OUTA, ">> $outfile_a");
	    printf OUTA  ("%-60s %6d  %11.5E %11.5E\n",$basename, $pt[4], $en[3], $en[6]);
	}
	elsif ($zz > 0 && $aa >0){
	    open(OUTZA, ">> $outfile_za");
	    printf OUTZA ("%-60s %6d  %11.5E %11.5E\n",$basename, $pt[4], $en[3], $en[6]);
	}
    }
}
