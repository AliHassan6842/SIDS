package com.agrosense.catalog.api;

import static com.agrosense.catalog.api.CatalogDtos.*;

import com.agrosense.catalog.domain.PestKind;
import com.agrosense.catalog.infrastructure.CatalogRepository;
import com.agrosense.shared.error.ApiException;
import java.util.List;
import java.util.UUID;
import org.springframework.web.bind.annotation.*;
import org.springframework.http.HttpStatus;

@RestController
@RequestMapping("/api/v1")
public class CatalogController {
    private final CatalogRepository catalog;
    public CatalogController(CatalogRepository catalog) 
    { this.catalog = catalog;
     }
    @GetMapping("/crops") 
    public List<CropResponse> crops(@RequestParam(defaultValue="false") boolean includeUnavailable) { return catalog.crops(includeUnavailable); 
    
    }

    @GetMapping("/pests")
     public List<PestResponse> pests(@RequestParam(required=false) PestKind kind,
                                                          @RequestParam(required=false) UUID cropId) {
        if (cropId != null && kind == PestKind.GENERAL_INSECT)
            throw new ApiException(HttpStatus.BAD_REQUEST, "INVALID_CATALOG_FILTER", "cropId cannot be used with GENERAL_INSECT.", false);
        PestKind effectiveKind = kind == null ? PestKind.CROP_PEST : kind;
        return catalog.pests(effectiveKind, cropId);
    }

    @GetMapping("/pests/{pestId}")
     public PestResponse pest(@PathVariable UUID pestId) 
     {
         return catalog.pest(pestId);
          }

    @GetMapping("/crops/{cropId}/pests") 
    public List<PestResponse> cropPests(@PathVariable UUID cropId) 
    {
         return catalog.pests(cropId); 
         
         }
}
