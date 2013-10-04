##### Auto-generated by parse_h_file.py ######### 
from ivi_defines import * 
def add_props(cls): 
    cls._new_attr('cache',                     IVI_ATTR_CACHE                        ,'ViBoolean',False,False,False)
    cls._new_attr('range_check',               IVI_ATTR_RANGE_CHECK                  ,'ViBoolean',False,False,False)
    cls._new_attr('query_instrument_status',   IVI_ATTR_QUERY_INSTRUMENT_STATUS      ,'ViBoolean',False,False,False)
    cls._new_attr('record_coercions',          IVI_ATTR_RECORD_COERCIONS             ,'ViBoolean',False,False,False)
    cls._new_attr('simulate',                  IVI_ATTR_SIMULATE                     ,'ViBoolean',False,False,False)
    cls._new_attr('interchange_check',         IVI_ATTR_INTERCHANGE_CHECK            ,'ViBoolean',False,False,False)
    cls._new_attr('spy',                       IVI_ATTR_SPY                          ,'ViBoolean',False,False,False)
    cls._new_attr('use_specific_simulation',   IVI_ATTR_USE_SPECIFIC_SIMULATION      ,'ViBoolean',False,False,False)
    cls._new_attr('group_capabilities',        IVI_ATTR_GROUP_CAPABILITIES           ,'ViString',False,False,True)
    cls._new_attr('function_capabilities',     IVI_ATTR_FUNCTION_CAPABILITIES        ,'ViString',False,False,True)
    cls._new_attr('class_driver_prefix',                         IVI_ATTR_CLASS_DRIVER_PREFIX                      ,'ViString',False,False,True)
    cls._new_attr('class_driver_vendor',                         IVI_ATTR_CLASS_DRIVER_VENDOR                      ,'ViString',False,False,True)
    cls._new_attr('class_driver_description',                    IVI_ATTR_CLASS_DRIVER_DESCRIPTION                 ,'ViString',False,False,True)
    cls._new_attr('class_driver_class_spec_major_version',       IVI_ATTR_CLASS_DRIVER_CLASS_SPEC_MAJOR_VERSION    ,'ViInt32',False,False,True)
    cls._new_attr('class_driver_class_spec_minor_version',       IVI_ATTR_CLASS_DRIVER_CLASS_SPEC_MINOR_VERSION    ,'ViInt32',False,False,True)
    cls._new_attr('specific_driver_prefix',                      IVI_ATTR_SPECIFIC_DRIVER_PREFIX                   ,'ViString',False,False,True)
    cls._new_attr('specific_driver_locator',                     IVI_ATTR_SPECIFIC_DRIVER_LOCATOR                  ,'ViString',False,False,True)
    cls._new_attr('io_resource_descriptor',                      IVI_ATTR_IO_RESOURCE_DESCRIPTOR                      ,'ViString',False,False,True)
    cls._new_attr('logical_name',                                IVI_ATTR_LOGICAL_NAME                             ,'ViString',False,False,True)
    cls._new_attr('specific_driver_vendor',                      IVI_ATTR_SPECIFIC_DRIVER_VENDOR                   ,'ViString',False,False,True)
    cls._new_attr('specific_driver_description',                 IVI_ATTR_SPECIFIC_DRIVER_DESCRIPTION              ,'ViString',False,False,True)
    cls._new_attr('specific_driver_class_spec_major_version',    IVI_ATTR_SPECIFIC_DRIVER_CLASS_SPEC_MAJOR_VERSION ,'ViInt32',False,False,True)
    cls._new_attr('specific_driver_class_spec_minor_version',    IVI_ATTR_SPECIFIC_DRIVER_CLASS_SPEC_MINOR_VERSION ,'ViInt32',False,False,True)
    cls._new_attr('instrument_firmware_revision',     IVI_ATTR_INSTRUMENT_FIRMWARE_REVISION  ,'ViString',False,False,True)
    cls._new_attr('instrument_manufacturer',          IVI_ATTR_INSTRUMENT_MANUFACTURER       ,'ViString',False,False,True)
    cls._new_attr('instrument_model',                 IVI_ATTR_INSTRUMENT_MODEL              ,'ViString',False,False,True)
    cls._new_attr('class_driver_revision',            IVI_ATTR_CLASS_DRIVER_REVISION         ,'ViString',False,False,True)
    cls._new_attr('specific_driver_revision',         IVI_ATTR_SPECIFIC_DRIVER_REVISION      ,'ViString',False,False,True)
    cls._new_attr('driver_setup',                     IVI_ATTR_DRIVER_SETUP                  ,'ViString',False,False,False)
    cls._new_attr('channel_count',             IVI_ATTR_CHANNEL_COUNT              ,'ViInt32',False,False,True)
    cls._new_attr('vertical_range',            (IVI_CLASS_PUBLIC_ATTR_BASE  + 1L)  ,'ViReal64',True,False,False)
    cls._new_attr('vertical_offset',           (IVI_CLASS_PUBLIC_ATTR_BASE  + 2L)  ,'ViReal64',True,False,False)
    cls._new_attr('vertical_coupling',         (IVI_CLASS_PUBLIC_ATTR_BASE  + 3L)  ,'ViInt32',True,False,False)
    cls._new_attr('probe_attenuation',         (IVI_CLASS_PUBLIC_ATTR_BASE  + 4L)  ,'ViReal64',True,False,False)
    cls._new_attr('channel_enabled',           (IVI_CLASS_PUBLIC_ATTR_BASE  + 5L)  ,'ViBoolean',True,False,False)
    cls._new_attr('max_input_frequency',       (IVI_CLASS_PUBLIC_ATTR_BASE  + 6L)  ,'ViReal64',True,False,False)
    cls._new_attr('input_impedance',           (IVI_CLASS_PUBLIC_ATTR_BASE  + 103L),'ViReal64',True,False,False)
    cls._new_attr('acquisition_type',          (IVI_CLASS_PUBLIC_ATTR_BASE  + 101L),'ViInt32',False,False,False)
    cls._new_attr('acquisition_start_time',    (IVI_CLASS_PUBLIC_ATTR_BASE  + 109L),'ViReal64',False,False,False)
    cls._new_attr('horz_time_per_record',      (IVI_CLASS_PUBLIC_ATTR_BASE  + 7L)  ,'ViReal64',False,False,False)
    cls._new_attr('horz_record_length',        (IVI_CLASS_PUBLIC_ATTR_BASE  + 8L)  ,'ViInt32',False,False,False)
    cls._new_attr('horz_min_num_pts',          (IVI_CLASS_PUBLIC_ATTR_BASE  + 9L)  ,'ViInt32',False,False,False)
    cls._new_attr('horz_sample_rate',          (IVI_CLASS_PUBLIC_ATTR_BASE  + 10L) ,'ViReal64',False,False,False)
    cls._new_attr('trigger_type',              (IVI_CLASS_PUBLIC_ATTR_BASE  + 12L) ,'ViInt32',False,False,False)
    cls._new_attr('trigger_source',            (IVI_CLASS_PUBLIC_ATTR_BASE  + 13L) ,'ViString',False,False,False)
    cls._new_attr('trigger_coupling',          (IVI_CLASS_PUBLIC_ATTR_BASE  + 14L) ,'ViInt32',False,False,False)
    cls._new_attr('trigger_holdoff',           (IVI_CLASS_PUBLIC_ATTR_BASE  + 16L) ,'ViReal64',False,False,False)
    cls._new_attr('trigger_level',             (IVI_CLASS_PUBLIC_ATTR_BASE  + 17L) ,'ViReal64',False,False,False)
    cls._new_attr('trigger_slope',             (IVI_CLASS_PUBLIC_ATTR_BASE  + 18L) ,'ViInt32',False,False,False)
    cls._new_attr('tv_trigger_signal_format',  (IVI_CLASS_PUBLIC_ATTR_BASE + 201L),'ViInt32',False,False,False)
    cls._new_attr('tv_trigger_event',          (IVI_CLASS_PUBLIC_ATTR_BASE + 205L),'ViInt32',False,False,False)
    cls._new_attr('tv_trigger_line_number',    (IVI_CLASS_PUBLIC_ATTR_BASE + 206L),'ViInt32',False,False,False)
    cls._new_attr('tv_trigger_polarity',       (IVI_CLASS_PUBLIC_ATTR_BASE + 204L),'ViInt32',False,False,False)
    cls._new_attr('runt_high_threshold',       (IVI_CLASS_PUBLIC_ATTR_BASE + 301L),'ViReal64',False,False,False)
    cls._new_attr('runt_low_threshold',        (IVI_CLASS_PUBLIC_ATTR_BASE + 302L),'ViReal64',False,False,False)
    cls._new_attr('runt_polarity',             (IVI_CLASS_PUBLIC_ATTR_BASE + 303L),'ViInt32',False,False,False)
    cls._new_attr('glitch_width',              (IVI_CLASS_PUBLIC_ATTR_BASE + 401L),'ViReal64',False,False,False)
    cls._new_attr('glitch_polarity',           (IVI_CLASS_PUBLIC_ATTR_BASE + 402L),'ViInt32',False,False,False)
    cls._new_attr('glitch_condition',          (IVI_CLASS_PUBLIC_ATTR_BASE + 403L),'ViInt32',False,False,False)
    cls._new_attr('width_low_threshold',       (IVI_CLASS_PUBLIC_ATTR_BASE + 501L),'ViReal64',False,False,False)
    cls._new_attr('width_high_threshold',      (IVI_CLASS_PUBLIC_ATTR_BASE + 502L),'ViReal64',False,False,False)
    cls._new_attr('width_polarity',            (IVI_CLASS_PUBLIC_ATTR_BASE + 503L),'ViInt32',False,False,False)
    cls._new_attr('width_condition',           (IVI_CLASS_PUBLIC_ATTR_BASE + 504L),'ViInt32',False,False,False)
    cls._new_attr('ac_line_trigger_slope',     (IVI_CLASS_PUBLIC_ATTR_BASE + 701L),'ViInt32',False,False,False)
    cls._new_attr('num_envelopes',             (IVI_CLASS_PUBLIC_ATTR_BASE + 105L),'ViInt32',False,False,False)
    cls._new_attr('meas_high_ref',             (IVI_CLASS_PUBLIC_ATTR_BASE + 607L),'ViReal64',False,False,False)
    cls._new_attr('meas_low_ref',              (IVI_CLASS_PUBLIC_ATTR_BASE + 608L),'ViReal64',False,False,False)
    cls._new_attr('meas_mid_ref',              (IVI_CLASS_PUBLIC_ATTR_BASE + 609L),'ViReal64',False,False,False)
    cls._new_attr('trigger_modifier',          (IVI_CLASS_PUBLIC_ATTR_BASE + 102L),'ViInt32',False,False,False)
    cls._new_attr('num_averages',              (IVI_CLASS_PUBLIC_ATTR_BASE + 104L),'ViInt32',False,False,False)
    cls._new_attr('sample_mode',               (IVI_CLASS_PUBLIC_ATTR_BASE + 106L),'ViInt32',False,False,False)
    cls._new_attr('initiate_continuous',       (IVI_CLASS_PUBLIC_ATTR_BASE + 107L),'ViBoolean',False,False,False)
    cls._new_attr('probe_sense_value',         (IVI_CLASS_PUBLIC_ATTR_BASE + 108L),'ViReal64',False,False,False)
    cls._new_attr('interpolation',             (IVI_CLASS_PUBLIC_ATTR_BASE  + 19L),'ViInt32',False,False,False)
