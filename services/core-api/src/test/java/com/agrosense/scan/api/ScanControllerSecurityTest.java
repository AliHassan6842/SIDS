package com.agrosense.scan.api;

import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

import com.agrosense.scan.application.ScanService;
import com.agrosense.shared.security.JwtAuthenticationFilter;
import com.agrosense.shared.security.JwtService;
import com.agrosense.shared.security.RateLimitFilter;
import com.agrosense.shared.security.SecurityConfig;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.webmvc.test.autoconfigure.WebMvcTest;
import org.springframework.boot.autoconfigure.ImportAutoConfiguration;
import org.springframework.boot.security.autoconfigure.web.servlet.ServletWebSecurityAutoConfiguration;
import org.springframework.context.annotation.Import;
import org.springframework.test.context.bean.override.mockito.MockitoBean;
import org.springframework.test.web.servlet.MockMvc;

@WebMvcTest(ScanController.class)
@Import({SecurityConfig.class, JwtAuthenticationFilter.class, RateLimitFilter.class})
@ImportAutoConfiguration(ServletWebSecurityAutoConfiguration.class)
class ScanControllerSecurityTest {
    @Autowired MockMvc mvc;
    @MockitoBean ScanService scans;
    @MockitoBean JwtService jwtService;

    @Test
    void anonymousUserCannotReadScanHistory() throws Exception {
        mvc.perform(get("/api/v1/scans")).andExpect(status().isForbidden());
    }
}
