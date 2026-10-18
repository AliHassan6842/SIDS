package com.agrosense.catalog.api;

import static com.agrosense.catalog.api.CatalogDtos.*;
import static org.mockito.Mockito.*;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

import com.agrosense.catalog.infrastructure.CatalogRepository;
import com.agrosense.catalog.domain.PestKind;
import com.agrosense.shared.error.GlobalExceptionHandler;
import java.util.List;
import java.util.UUID;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.test.web.servlet.setup.MockMvcBuilders;

class CatalogControllerTest {
    private CatalogRepository catalog;
    private MockMvc mvc;

    @BeforeEach
    void setUp() {
        catalog = mock(CatalogRepository.class);
        mvc = MockMvcBuilders.standaloneSetup(new CatalogController(catalog))
            .setControllerAdvice(new GlobalExceptionHandler()).build();
    }

    @Test
    void bindsPestUuidFromPublicRoute() throws Exception {
        UUID pestId = UUID.randomUUID();
        when(catalog.pest(pestId)).thenReturn(pest(pestId));

        mvc.perform(get("/api/v1/pests/{pestId}", pestId)).andExpect(status().isOk());

        verify(catalog).pest(pestId);
    }

    @Test
    void bindsCropUuidWhenFilteringSupportedPests() throws Exception {
        UUID cropId = UUID.randomUUID();
        when(catalog.pests(cropId)).thenReturn(List.of());

        mvc.perform(get("/api/v1/crops/{cropId}/pests", cropId)).andExpect(status().isOk());

        verify(catalog).pests(cropId);
    }

    @Test
    void defaultsUnfilteredCatalogToCropPests() throws Exception {
        when(catalog.pests(PestKind.CROP_PEST, null)).thenReturn(List.of());

        mvc.perform(get("/api/v1/pests")).andExpect(status().isOk());

        verify(catalog).pests(PestKind.CROP_PEST, null);
    }

    @Test
    void explicitlyListsGeneralInsectCatalog() throws Exception {
        when(catalog.pests(PestKind.GENERAL_INSECT, null)).thenReturn(List.of());

        mvc.perform(get("/api/v1/pests").queryParam("kind", "GENERAL_INSECT"))
            .andExpect(status().isOk());

        verify(catalog).pests(PestKind.GENERAL_INSECT, null);
    }

    @Test
    void rejectsCropFilterForGeneralInsects() throws Exception {
        mvc.perform(get("/api/v1/pests").queryParam("kind", "GENERAL_INSECT")
                .queryParam("cropId", UUID.randomUUID().toString()))
            .andExpect(status().isBadRequest());

        verifyNoInteractions(catalog);
    }

    @Test
    void rejectsMalformedPublicPestUuid() throws Exception {
        mvc.perform(get("/api/v1/pests/not-a-uuid")).andExpect(status().isBadRequest());

        verifyNoInteractions(catalog);
    }

    private PestResponse pest(UUID id) {
        return new PestResponse(id, "rice-leaf-roller", "Rice leaf roller", "Cnaphalocrocis medinalis",
            "Rice pest", List.of(), null);
    }
}
