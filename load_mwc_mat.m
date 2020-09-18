function out = load_mat( matfile )

m = load(matfile);

% Walk through MWC struture
out.mwc = cell2struct( m.MWC, {'temppings'}, 2 );

for p = 1:numel(out.mwc)
  out.mwc(p).tempbeams = cell2struct( out.mwc(p).temppings.beams, {'tempbeams'}, 2);

  %
  % This is frustratingly manual
  %
  for b = 1:numel(out.mwc(p).tempbeams)
    out.mwc(p).beams(b).beamPointAngReVertical_deg = out.mwc(p).tempbeams(b).tempbeams.beamPointAngReVertical_deg;
    out.mwc(p).beams(b).sampleAmplitude05dB_p      = out.mwc(p).tempbeams(b).tempbeams.sampleAmplitude05dB_p;
    out.mwc(p).beams(b).rxBeamPhase_deg            = out.mwc(p).tempbeams(b).tempbeams.rxBeamPhase_deg;
  end

end

out.mwc = rmfield( out.mwc, {'tempbeams', 'temppings'} );
