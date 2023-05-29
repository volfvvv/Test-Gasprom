#!/usr/bin/perl

#filter.pl;
##################
##  анализ логфайла out(имя может быть передано в командной строке) и запись данных в таблицы
##################
use DBI;
use strict;

# имя базы данных
my $dbname = "volk";
# имя пользователя
my $username = "postgres";
# пароль
my $password = "1";
# имя или IP адрес сервера
my $dbhost = "localhost";
# порт
my $dbport = "5432";
# опции
my $dboptions = "-e";
# терминал
my $dbtty = "ansi";

my $dbh = DBI->connect("dbi:Pg:dbname=$dbname;options=$dboptions;tty=$dbtty","$username","$password",
		    {PrintError => 0});

if ($DBI::err != 0) {
  print $DBI::errstr . "\n";
  exit($DBI::err);
}



my %flags = setub_available_flags(); # заранее в хэш помещены все возмоджные флаги

my $file = $ARGV[0] | 'out';

open(F, '<', $file);

$dbh->do('truncate message');
$dbh->do('truncate log');

$dbh->begin_work();


while ($_=<F>){
	chomp $_;
	
	my @a = split / /, $_, 5;
	
	my $ts = "$a[0] $a[1]";
	my $flag = $a[3];
	my $int_id = $a[2];
	my $found = 0;
	my $str = qq/$a[2] $a[3] $a[4]/;
	$str =~ s/'/''/g;				# экранирование апострофа
	if (exists $flags{$flag}){		# есть флаг
		if ($flag eq '<='){			# и он равен '<='
			my ($id) = ($a[4] =~ m/id=(\S+)/);		# выделяем id
			if ($id) {  							# если id не указан записывать в message нельзя, т.к. будет нарушен констрейнт NOT NULL
				$found = 1;							# указывает, что запись прошла в message
				my $query = "INSERT INTO message(created, id, int_id, str) VALUES ('$ts', '$id', '$int_id', '$str')";
				$dbh->do($query);
			}
		}
	}
	unless ($found){	# запись не прошла в message, значит записываем в log
		my $address;
		my $query;
		if (exists $flags{$flag}){
			$address = $a[4];
			$address =~ s/'/''/g;				# экранирование апострофа на всякий случай
			$query = "INSERT INTO log(created, int_id, str, address) VALUES ('$ts', '$int_id', '$str', '$address')";
		} else{
			$query = "INSERT INTO log(created, int_id, str) VALUES ('$ts', '$int_id', '$str')";
		}
		$dbh->do($query);
	}
	if ($DBI::err != 0) {
	  print $DBI::errstr . "\n";
	  exit($DBI::err);
	}	
}

$dbh->commit();
$dbh->disconnect();




sub setub_available_flags{ # чтение флагов из их описания

	my $flags_str =<<EOF
<= прибытие сообщения (в этом случае за флагом следует адрес отправителя)
=> нормальная доставка сообщения
-> дополнительный адрес в той же доставке
** доставка не удалась
== доставка задержана (временная проблема)
EOF
	;
	
	my %flags;
	my @a = split /\n/, $flags_str;
	map{
		if ($_){
			s/(..).*/$1/;
			$flags{$_} = 1;
		}
	} @a;
	return %flags;
}

1;
