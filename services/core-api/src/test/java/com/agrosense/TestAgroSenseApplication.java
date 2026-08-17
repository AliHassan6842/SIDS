package com.agrosense;

import org.springframework.boot.SpringApplication;

public class TestAgroSenseApplication {

	public static void main(String[] args) {
		SpringApplication.from(AgroSenseApplication::main).with(TestcontainersConfiguration.class).run(args);
	}

}
