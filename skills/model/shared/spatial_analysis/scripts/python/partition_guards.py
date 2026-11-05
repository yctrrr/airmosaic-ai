"""Conditional angular-distance and positive-source-node partition checks."""
import numpy as np


def check_partition(points,train_ids,validation_ids,weights_by_family,*,guard_km,radius_km,coordinate_basis):
    """Check a frozen partition; never assign folds or verify unknown metadata.

    points is indexed by unique string point IDs with longitude/latitude columns.
    Weights retain point_id/source_x/source_y/weight. Distances use the explicitly
    declared sphere; geographic accuracy is conditional on coordinate metadata.
    """
    if coordinate_basis!='angular_lon_lat_aligned_without_verified_datum':raise ValueError('explicit_coordinate_basis_required')
    if not 0<=guard_km<10000 or not 6000<radius_km<7000:raise ValueError('invalid_distance_contract')
    train_ids=list(train_ids);validation_ids=list(validation_ids)
    if (not train_ids or not validation_ids or len(set(train_ids))!=len(train_ids)
            or len(set(validation_ids))!=len(validation_ids) or set(train_ids)&set(validation_ids)
            or not points.index.is_unique):raise ValueError('invalid_partition_ids')
    a=points.loc[train_ids,['longitude','latitude']].to_numpy(dtype=float)
    b=points.loc[validation_ids,['longitude','latitude']].to_numpy(dtype=float)
    if (not np.isfinite(a).all() or not np.isfinite(b).all() or (np.abs(a[:,1])>90).any()
            or (np.abs(b[:,1])>90).any()):raise ValueError('invalid_partition_coordinates')
    a=np.radians(a);b=np.radians(b);distance=float('inf')
    for start in range(0,len(a),128):
        lon=a[start:start+128,0,None];lat=a[start:start+128,1,None]
        q=np.sin((lat-b[None,:,1])/2)**2+np.cos(lat)*np.cos(b[None,:,1])*np.sin((lon-b[None,:,0])/2)**2
        distance=min(distance,float(np.min(2*radius_km*np.arcsin(np.sqrt(np.clip(q,0,1))))))
    overlap={}
    if not weights_by_family:raise ValueError('source_weights_required')
    for family,weights in weights_by_family.items():
        if not set(train_ids+validation_ids)<=set(weights.point_id):raise ValueError('missing_source_support_identity')
        if (weights.weight.isna().any() or (weights.weight<0).any() or not np.isfinite(weights[['source_x','source_y','weight']].to_numpy(dtype=float)).all()):
            raise ValueError('invalid_source_support')
        positive=weights.loc[weights.weight.gt(0)]
        if not set(train_ids+validation_ids)<=set(positive.point_id):
            raise ValueError('missing_positive_source_support')
        def nodes(ids):return set(map(tuple,positive.loc[positive.point_id.isin(ids),['source_x','source_y']].to_numpy()))
        overlap[family]=len(nodes(train_ids)&nodes(validation_ids))
    return {'passed':distance>=guard_km and not any(overlap.values()),'nearest_km':distance,
        'shared_positive_nodes':overlap,'train_points':len(train_ids),'validation_points':len(validation_ids),
        'coordinate_metadata_verified':False,'radius_km':radius_km,'guard_km':guard_km}
