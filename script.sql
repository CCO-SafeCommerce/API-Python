CREATE DATABASE bdSafeCommerce;

USE bdSafeCommerce;

CREATE TABLE servidor(
	id INT PRIMARY KEY AUTO_INCREMENT
);

CREATE TABLE processo(
	id INT PRIMARY KEY AUTO_INCREMENT
    ,nome VARCHAR(40)
    ,porcentagemCpu DECIMAL(5,2)
    ,fkServidor INT
    ,FOREIGN KEY (fkServidor) REFERENCES servidor(id)
	,horario DATETIME
);

SELECT porcentagemCpu, DATE_FORMAT(horario, '%e %b, %H:%i %s') AS horario FROM processo 
	WHERE fkServidor = 1
	ORDER BY horario DESC
    limit 7;

CREATE TABLE ram(
	id INT PRIMARY KEY AUTO_INCREMENT
    ,totalMemoria DECIMAL(5,2)
    ,porcentagemUso DECIMAL(5,2)
    ,fkServidor INT
    ,FOREIGN KEY (fkServidor) REFERENCES servidor(id)
    ,horario DATETIME
);

CREATE TABLE swap(
	id INT PRIMARY KEY AUTO_INCREMENT
    ,totalMemoria DECIMAL(5,2)
    ,porcentagemUso DECIMAL(5,2)
    ,fkServidor INT
    ,FOREIGN KEY (fkServidor) REFERENCES servidor(id)
	,horario DATETIME
);

CREATE TABLE HistoricoCpu(
	id INT PRIMARY KEY AUTO_INCREMENT
    ,porcentagemUso DECIMAL(5,2)
    ,qtdProcessos INT
    ,fkServidor INT
    ,FOREIGN KEY (fkServidor) REFERENCES servidor(id)
    ,horario DATETIME
);

CREATE TABLE disco(
	id INT PRIMARY KEY AUTO_INCREMENT
    ,porcentagemUso DECIMAL(5,2)
    ,lido DECIMAL(5,2) 
    ,escreveu DECIMAL(5,2)
    ,fkServidor INT
    ,FOREIGN KEY (fkServidor) REFERENCES servidor(id)
    ,horario DATETIME
);