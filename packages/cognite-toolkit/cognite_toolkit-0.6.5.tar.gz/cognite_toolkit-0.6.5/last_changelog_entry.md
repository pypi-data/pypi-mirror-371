## cdf 

### Removed

- [alpha] In the `cdf migrate timeseries/files` the mapping file must
now be `id,space,externalId` or `id,dataSetId,space,externalId`. You can
no longer have `externalId` in the first column to reference the
asset-centric timeseries/file. The reason is to simplify the use and
make the file only have one valid way of referencing asset-centric
resources, and thus cause less confusion.

## templates

No changes.